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

"""
This module contains the VersionTagCheckAction class which is the main entry point for the GitHub Action.
"""
import logging
import sys

from version_tag_check.github_repository import GitHubRepository
from version_tag_check.utils.gh_action import get_action_input, set_action_failed
from version_tag_check.version import Version
from version_tag_check.version_validator import NewVersionValidator

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class VersionTagCheckAction:
    """
    Class to handle the Version Tag Check GitHub Action
    """

    def __init__(self) -> None:
        """
        Initialize the action with the required inputs.

        @return: None
        """
        self.github_token: str = get_action_input("GITHUB_TOKEN", "")
        self.version_tag_str: str = get_action_input("VERSION_TAG", "")
        self.github_repository: str = get_action_input("GITHUB_REPOSITORY", "")
        self.should_exist: bool = get_action_input("SHOULD_EXIST", "false").lower() == "true"

        self.__validate_inputs()

        self.owner, self.repo = self.github_repository.split("/")

    def run(self) -> None:
        """
        Run the action.

        @return: None
        """
        new_version = Version(self.version_tag_str)
        if not new_version.is_valid_format():
            set_action_failed('Tag does not match the required format "v[0-9]+.[0-9]+.[0-9]+"')

        repository: GitHubRepository = GitHubRepository(self.owner, self.repo, self.github_token)
        existing_versions: list[Version] = repository.get_all_tags()

        # check if the tag exists in repository
        if new_version in existing_versions:
            # it exists, check if not expected
            if not self.should_exist:
                set_action_failed("The tag already exists in the repository.")
        else:
            # it does not exist, check if expected
            if self.should_exist:
                set_action_failed("The tag does not exist in the repository.")

        # if expected to exist, exit here, no more checks expected to be done
        if self.should_exist:
            sys.exit(0)

        validator = NewVersionValidator(new_version, existing_versions)
        if validator.is_valid_increment():
            logger.info("New tag is valid increment.")
            sys.exit(0)
        else:
            set_action_failed("New tag is not valid increment.")

    def __validate_inputs(self) -> None:
        """
        Validate the required inputs. When the inputs are not valid, the action will fail.

        @return: None
        """
        if len(self.github_token) == 0:
            set_action_failed("Failure: GITHUB_TOKEN is not set correctly.")

        if not self.github_repository:
            set_action_failed("Failure: GITHUB_REPOSITORY is not set correctly.")

        if len(self.version_tag_str) == 0:
            set_action_failed("Failure: VERSION_TAG is not set correctly.")
