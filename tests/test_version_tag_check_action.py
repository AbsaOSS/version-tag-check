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
import pytest

from version_tag_check.version_tag_check_action import VersionTagCheckAction


# input validation

@pytest.mark.parametrize("missing_var, error_message", [
    ("INPUT_GITHUB_TOKEN", "Failure: GITHUB_TOKEN is not set correctly."),
    ("INPUT_GITHUB_REPOSITORY", "Failure: GITHUB_REPOSITORY is not set correctly."),
    ("INPUT_VERSION_TAG", "Failure: VERSION_TAG is not set correctly."),
])
def test_validate_inputs_missing_variables(monkeypatch, caplog, missing_var, error_message):
    # Set all required environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_VERSION_TAG": "v1.0.0",
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

@pytest.mark.parametrize(
    "version_tag, existing_tags",
    [
        ("v0.0.1", []),                         # New version with no existing tags
        ("v0.1.0", []),                         # New version with no existing tags
        ("v1.0.0", []),                         # New version with no existing tags
        ("v0.0.2", ["v0.0.1"]),                 # Patch increment
        ("v1.2.0", ["v1.1.0"]),                 # Minor increment
        ("v2.0.0", ["v1.9.9"]),                 # Major increment
        ("v2.1.0", ["v2.0.5", "v2.0.0"]),       # New Release serie
        ("v3.0.1", ["v2.9.9", "v1.0.0"]),       # Increment with Gaps
        ("v1.5.2", ["v2.0.0", "v1.5.1"]),       # Backport increment
    ],
)
def test_run_successful(mocker, version_tag, existing_tags):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": version_tag,
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
    }
    os.environ.update(env_vars)

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit")

    # Mock the Version class
    mock_version_class = mocker.patch("version_tag_check.version_tag_check_action.Version")
    mock_version_instance = mock_version_class.return_value
    mock_version_instance.is_valid_format.return_value = True

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("version_tag_check.version_tag_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_all_tags.return_value = existing_tags

    # Mock the NewVersionValidator class
    mock_validator_class = mocker.patch("version_tag_check.version_tag_check_action.NewVersionValidator")
    mock_validator_instance = mock_validator_class.return_value
    mock_validator_instance.is_valid_increment.return_value = True

    # Run the action
    action = VersionTagCheckAction()
    action.run()

    mock_exit.assert_called_once_with(0)


@pytest.mark.parametrize(
    "version_tag, existing_tags, is_valid_format, is_valid_increment, expected_exit_code, error_message",
    [
        ("invalid_version", [], False, True, 1, "Tag does not match the required format"),  # Invalid format
        ("invalid_version", ["v1.0.0"], False, True, 1, "Tag does not match the required format"),  # Invalid format
        ("v1.0.3", ["v1.0.1"], True, False, 1, "New tag is not valid."),                    # Invalid increment
        ("v1.0.0", ["v1.0.0"], True, False, 1, "New tag is not valid."),                    # Existing tag
        ("v1.4.1", ["v2.0.0", "v1.4.2"], True, False, 1, "New tag is not valid."),          # Invalid backport increment
        ("1.0.0", [], False, True, 1, "Tag does not match the required format"),          # Invalid format and increment
    ],
)
def test_run_unsuccessful(mocker, caplog, version_tag, existing_tags, is_valid_format, is_valid_increment, expected_exit_code, error_message):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": version_tag,
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
    }
    os.environ.update(env_vars)

    # Mock sys.exit to raise a SystemExit for assertion
    def mock_exit(code):
        raise SystemExit(code)

    mocker.patch("sys.exit", mock_exit)

    # Mock the Version class
    mock_version_class = mocker.patch("version_tag_check.version_tag_check_action.Version")
    mock_version_instance = mock_version_class.return_value
    mock_version_instance.is_valid_format.return_value = is_valid_format

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("version_tag_check.version_tag_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_all_tags.return_value = existing_tags

    # Mock the NewVersionValidator class
    mock_validator_class = mocker.patch("version_tag_check.version_tag_check_action.NewVersionValidator")
    mock_validator_instance = mock_validator_class.return_value
    mock_validator_instance.is_valid_increment.return_value = is_valid_increment

    # Run the action
    caplog.set_level(logging.ERROR)
    action = VersionTagCheckAction()
    with pytest.raises(SystemExit) as e:
        action.run()

    # Assert sys.exit was called with the correct code
    assert e.value.code == expected_exit_code

    # Assert error message in logs
    assert error_message in caplog.text
