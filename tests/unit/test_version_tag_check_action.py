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

from version_tag_check.utils.constants import ERROR_TAG_ALREADY_EXISTS, ERROR_TAG_DOES_NOT_EXIST
from version_tag_check.version import Version
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
    "version_tag, should_exist, existing_tags",
    [
        ("v0.0.1", "false", []),                                             # New version with no existing tags
        ("v0.1.0", "false", []),                                             # New version with no existing tags
        ("v1.0.0", "false", []),                                             # New version with no existing tags
        ("v0.0.2", "false", [Version("v0.0.1")]),                            # Patch increment
        ("v1.2.0", "false", [Version("v1.1.0")]),                            # Minor increment
        ("v2.0.0", "false", [Version("v1.9.9")]),                            # Major increment
        ("v2.1.0", "false", [Version("v2.0.5"), Version("v2.0.0")]),         # New Release serie
        ("v1.5.2", "false", [Version("v2.0.0"), Version("v1.5.1")]),         # Backport increment
    ],
)
def test_run_successful_should_not_exist(mocker, version_tag, should_exist, existing_tags):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": version_tag,
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_SHOULD_EXIST": should_exist,
    }
    os.environ.update(env_vars)

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit")

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("version_tag_check.version_tag_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_all_tags.return_value = existing_tags

    # Run the action
    action = VersionTagCheckAction()
    action.run()

    mock_exit.assert_called_once_with(0)


@pytest.mark.parametrize(
    "version_tag, should_exist, existing_tags",
    [
        ("v0.0.1", "true", [Version("v0.0.1")]),                             # check existence of tag - should exist
    ],
)
def test_run_successful_should_exist(mocker, version_tag, should_exist, existing_tags):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": version_tag,
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_SHOULD_EXIST": should_exist,
    }
    os.environ.update(env_vars)

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("version_tag_check.version_tag_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_all_tags.return_value = existing_tags

    # Run the action
    action = VersionTagCheckAction()
    with pytest.raises(SystemExit) as e:
        action.run()

    assert 0 == e.value.code


@pytest.mark.parametrize(
    "version_tag, should_exist, existing_tags, is_valid_format, is_valid_increment, expected_exit_code, error_message",
    [
        ("invalid_version", "false", [], False, True, 1, "Version 'invalid_version' does not match the required format"),                                                              # Invalid format
        ("invalid_version", "false", [Version("v1.0.0")], False, True, 1, "Version 'invalid_version' does not match the required format"),                                             # Invalid format
        ("v1.0.3", "false", [Version("v1.0.1")], True, False, 1, "New tag v1.0.3 is not one patch higher than the latest tag v1.0.1."),                          # Invalid increment
        ("v1.0.2", "true", [Version("v1.0.1")], True, False, 1, ERROR_TAG_DOES_NOT_EXIST),                                                    # Tag should exist
        ("v1.0.0", "false", [Version("v1.0.0")], True, False, 1, ERROR_TAG_ALREADY_EXISTS),                                                    # Tag already exists
        ("v1.4.1", "false", [Version("v2.0.0"), Version("v1.4.2")], True, False, 1, "New tag v1.4.1 is not one patch higher than the latest tag v1.4.2."),       # Invalid backport increment
        ("1.0.0", "false", [], False, True, 1, "Version '1.0.0' does not match the required format"),                                                                        # Invalid format and increment
        ("v3.0.1", "false", [Version("v2.9.9"), Version("v1.0.0")], True, False, 1, "New tag v3.0.1 is not a valid major bump. Latest version: v2.9.9."),        # Invalid version gap
    ],
)
def test_run_unsuccessful(mocker, caplog, version_tag, should_exist, existing_tags, is_valid_format, is_valid_increment, expected_exit_code, error_message):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": version_tag,
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_SHOULD_EXIST": should_exist,
    }
    os.environ.update(env_vars)

    # Mock sys.exit to raise a SystemExit for assertion
    def mock_exit(code):
        raise SystemExit(code)

    mocker.patch("sys.exit", mock_exit)

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("version_tag_check.version_tag_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_all_tags.return_value = existing_tags

    # Run the action
    caplog.set_level(logging.ERROR)
    action = VersionTagCheckAction()
    with pytest.raises(SystemExit) as e:
        action.run()

    # Assert sys.exit was called with the correct code
    assert e.value.code == expected_exit_code

    # Assert error message in logs
    assert error_message in caplog.text


# Tests for qualifier support

@pytest.mark.parametrize(
    "version_tag, should_exist, existing_tags",
    [
        ("v1.0.0-SNAPSHOT", "false", []),                                        # First version with qualifier
        ("v1.0.0-ALPHA", "false", [Version("v1.0.0-SNAPSHOT")]),                 # Qualifier progression
        ("v1.0.0-BETA", "false", [Version("v1.0.0-ALPHA")]),                     # Qualifier progression
        ("v1.0.0-RC1", "false", [Version("v1.0.0-BETA")]),                       # Qualifier progression
        ("v1.0.0-RC2", "false", [Version("v1.0.0-RC1")]),                        # RC progression
        ("v1.0.0-RELEASE", "false", [Version("v1.0.0-RC2")]),                    # Qualifier progression
        ("v1.0.0", "false", [Version("v1.0.0-RELEASE")]),                        # Release to bare
        ("v1.0.0-HF1", "false", [Version("v1.0.0")]),                            # Hotfix after release
        ("v1.0.0-HF2", "false", [Version("v1.0.0-HF1")]),                        # HF progression
    ],
)
def test_run_successful_with_qualifiers(mocker, version_tag, should_exist, existing_tags):
    """Test that the action handles version tags with valid qualifiers"""
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": version_tag,
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_SHOULD_EXIST": should_exist,
    }
    os.environ.update(env_vars)

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit")

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("version_tag_check.version_tag_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_all_tags.return_value = existing_tags

    # Run the action
    action = VersionTagCheckAction()
    action.run()

    mock_exit.assert_called_once_with(0)


@pytest.mark.parametrize(
    "version_tag, expected_error",
    [
        ("v1.0.0-UNKNOWN", "Invalid qualifier 'UNKNOWN'"),
        ("v1.0.0-RC", "Invalid qualifier 'RC'"),
        ("v1.0.0-RC0", "Invalid qualifier 'RC0'"),
        ("v1.0.0-RC100", "Invalid qualifier 'RC100'"),
        ("v1.0.0-HF", "Invalid qualifier 'HF'"),
        ("v1.0.0-HF0", "Invalid qualifier 'HF0'"),
        ("v1.0.0-SNAPSHOT1", "Invalid qualifier 'SNAPSHOT1'"),
        ("v1.0.0-SNAPSHOT2", "Invalid qualifier 'SNAPSHOT2'"),
        ("v1.0.0-ALPHA1", "Invalid qualifier 'ALPHA1'"),
        ("v1.0.0-ALPHA2", "Invalid qualifier 'ALPHA2'"),
        ("v1.0.0-BETA1", "Invalid qualifier 'BETA1'"),
        ("v1.0.0-BETA2", "Invalid qualifier 'BETA2'"),
        ("v1.0.0-RELEASE1", "Invalid qualifier 'RELEASE1'"),
        ("v1.0.0-RELEASE2", "Invalid qualifier 'RELEASE2'"),
    ],
)
def test_run_invalid_qualifier(mocker, caplog, version_tag, expected_error):
    """Test that the action rejects version tags with invalid qualifiers"""
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_VERSION_TAG": version_tag,
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_SHOULD_EXIST": "false",
    }
    os.environ.update(env_vars)

    # Mock sys.exit to raise a SystemExit for assertion
    def mock_exit(code):
        raise SystemExit(code)

    mocker.patch("sys.exit", mock_exit)

    # Mock the GitHubRepository class (won't be called due to early failure)
    mock_repository_class = mocker.patch("version_tag_check.version_tag_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_all_tags.return_value = []

    # Run the action
    caplog.set_level(logging.ERROR)
    action = VersionTagCheckAction()
    with pytest.raises(SystemExit) as e:
        action.run()

    # Assert sys.exit was called with code 1
    assert e.value.code == 1

    # Assert error message in logs
    assert expected_error in caplog.text
