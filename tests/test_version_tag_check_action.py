#
# Copyright 2024 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from version_tag_check.version_tag_check_action import VersionTagCheckAction


# input validation

@pytest.mark.parametrize("missing_var, error_message", [
    ("INPUT_GITHUB_TOKEN", "Failure: GITHUB_TOKEN is not set correctly."),
    ("INPUT_GITHUB_REPOSITORY", "Failure: GITHUB_REPOSITORY is not set correctly."),
    ("INPUT_VERSION_TAG", "Failure: VERSION_TAG is not set correctly."),
    ("INPUT_BRANCH", "Failure: BRANCH is not set correctly."),
])
def test_validate_inputs_missing_variables(monkeypatch, caplog, missing_var, error_message):
    # Set all required environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_VERSION_TAG": "v1.0.0",
        "INPUT_BRANCH": "main",
    }
    env_vars.pop(missing_var)  # Remove the variable to test
    if missing_var in os.environ.keys():
        os.environ.pop(missing_var)
    os.environ.update(env_vars)

    # Mock sys.exit to raise SystemExit exception
    with pytest.raises(SystemExit) as e:
        # Capture logs
        caplog.set_level(logging.ERROR)

        # Instantiate the action; should raise SystemExit
        VersionTagCheckAction()

    # Assert that sys.exit was called with exit code 1
    assert e.value.code == 1

    # Assert that the correct error message was logged
    assert error_message in caplog.text


# run

def test_run_successful(mocker, tmp_path):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": "v1.0.1",
        "INPUT_BRANCH": "main",
        "INPUT_FAILS_ON_ERROR": "true",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
    }
    # Update os.environ with the test environment variables
    os.environ.update(env_vars)
    if os.path.exists("output.txt"):
        os.remove("output.txt")

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit")

    # Mock the Version class
    mock_version_class = mocker.patch("version_tag_check.version_tag_check_action.Version")
    mock_version_instance = mock_version_class.return_value
    mock_version_instance.is_valid_format.return_value = True

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("version_tag_check.version_tag_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_all_tags.return_value = []

    # Mock the NewVersionValidator class
    mock_validator_class = mocker.patch("version_tag_check.version_tag_check_action.NewVersionValidator")
    mock_validator_instance = mock_validator_class.return_value
    mock_validator_instance.is_valid_increment.return_value = True

    # Run the action
    action = VersionTagCheckAction()
    action.run()

    # Assert that 'valid=true' was written to the output file
    output_file = Path("output.txt")
    assert output_file.read_text() == "valid=true\n"

    # Assert that sys.exit was called with 0
    mock_exit.assert_called_once_with(0)

def test_run_invalid_version_format(mocker, tmp_path, caplog):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": "invalid_version",
        "INPUT_BRANCH": "main",
        "INPUT_FAILS_ON_ERROR": "true",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
    }
    os.environ.update(env_vars)
    if os.path.exists("output.txt"):
        os.remove("output.txt")

    # Mock sys.exit
    def mock_exit(code):
        raise SystemExit(code)

    mocker.patch("sys.exit", mock_exit)

    # Mock the Version class used in VersionTagCheckAction
    mock_version_class = mocker.patch("version_tag_check.version_tag_check_action.Version")
    mock_version_instance = mock_version_class.return_value
    mock_version_instance.is_valid_format.return_value = False  # Simulate invalid format

    # Run the action
    caplog.set_level(logging.ERROR)
    action = VersionTagCheckAction()
    with pytest.raises(SystemExit) as e:
        action.run()

    # Assert that sys.exit was called with exit code 1
    assert e.value.code == 1

    # Assert that 'valid=false' was written to the output file
    output_file = Path("output.txt")
    assert output_file.read_text() == "valid=false\n"

    # Assert that an error was logged
    assert 'Tag does not match the required format' in caplog.text

def test_run_invalid_version_increment(mocker, tmp_path):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": "v1.0.2",
        "INPUT_BRANCH": "main",
        "INPUT_FAILS_ON_ERROR": "true",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
    }
    os.environ.update(env_vars)
    if os.path.exists("output.txt"):
        os.remove("output.txt")

    # Mock sys.exit
    mock_exit = mocker.patch("sys.exit")

    # Mock the Version class
    mock_version_class = mocker.patch("version_tag_check.version_tag_check_action.Version")
    mock_version_instance = mock_version_class.return_value
    mock_version_instance.is_valid_format.return_value = True

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("version_tag_check.version_tag_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_all_tags.return_value = []  # Simulate existing versions if needed

    # Mock the NewVersionValidator class to return False for is_valid_increment
    mock_validator_class = mocker.patch("version_tag_check.version_tag_check_action.NewVersionValidator")
    mock_validator_instance = mock_validator_class.return_value
    mock_validator_instance.is_valid_increment.return_value = False

    # Run the action
    action = VersionTagCheckAction()
    action.run()

    # Assert that 'valid=false' was written to the output file
    output_file = Path("output.txt")
    assert output_file.read_text() == "valid=false\n"

    # Assert that sys.exit was called with 1
    mock_exit.assert_called_once_with(1)


# handle_failure

def test_handle_failure_fails_on_error_false(mocker):
    # Set environment variables with 'INPUT_FAILS_ON_ERROR' set to 'false'
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": "v1.0.0",
        "INPUT_BRANCH": "main",
        "INPUT_FAILS_ON_ERROR": "false",  # Set to 'false' to test else branch
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
    }
    mocker.patch.dict(os.environ, env_vars)

    # Mock sys.exit to raise SystemExit exception
    def mock_exit(code):
        raise SystemExit(code)
    mocker.patch("sys.exit", mock_exit)

    # Instantiate the action
    action = VersionTagCheckAction()

    # Call handle_failure and expect SystemExit
    with pytest.raises(SystemExit) as e:
        action.handle_failure()

    # Assert that sys.exit was called with exit code 0
    assert e.value.code == 0
