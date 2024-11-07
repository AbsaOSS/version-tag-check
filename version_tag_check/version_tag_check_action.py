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
import os
import sys

from version_tag_check.github_repository import GitHubRepository
from version_tag_check.version import Version
from version_tag_check.version_validator import VersionValidator

logger = logging.getLogger(__name__)


class VersionTagCheckAction:
    """
    Class to handle the Version Tag Check GitHub Action
    """

    def __init__(self) -> None:
        """
        Initialize the action with the required inputs.

        @return: None
        """
        self.github_token = os.environ.get("INPUT_GITHUB_TOKEN")
        self.version_tag_str = os.environ.get("INPUT_VERSION_TAG")
        self.branch = os.environ.get("INPUT_BRANCH")
        self.fails_on_error = os.environ.get("INPUT_FAILS_ON_ERROR", "true").lower() == "true"
        self.github_repository = os.environ.get("INPUT_GITHUB_REPOSITORY")

        self.__validate_inputs()

        self.owner, self.repo = self.github_repository.split("/")

    def run(self) -> None:
        """
        Run the action.

        @return: None
        """
        try:
            new_version = Version(self.version_tag_str)
            if not new_version.is_valid_format():
                logger.error('Tag does not match the required format "v[0-9]+.[0-9]+.[0-9]+"')
                self.handle_failure()

            repository = GitHubRepository(self.owner, self.repo, self.github_token)
            existing_versions = repository.get_all_tags()

            validator = VersionValidator(new_version, existing_versions)
            if validator.is_valid_increment():
                self.write_output("true")
                logger.info("New tag is valid.")
                sys.exit(0)
            else:
                latest_version = validator.get_latest_version()
                logger.error(
                    "New tag %s is not one version higher than the latest tag %s.", self.version_tag_str, latest_version
                )
                self.handle_failure()

        except ValueError as e:
            logger.error(str(e))
            self.handle_failure()

    def write_output(self, valid_value) -> None:
        """
        Write the output to the file specified by the GITHUB_OUTPUT environment variable.

        @param valid_value: The value to write to the output file.
        @return: None
        """
        output_file = os.environ.get("GITHUB_OUTPUT")
        if output_file:
            with open(output_file, "a", encoding="utf-8") as fh:
                print(f"valid={valid_value}", file=fh)
        else:
            logger.error("GITHUB_OUTPUT is not set.")

    def handle_failure(self) -> None:
        """
        Handle the failure of the action.

        @return: None
        """
        self.write_output("false")
        if self.fails_on_error:
            sys.exit(1)
        else:
            sys.exit(0)

    def __validate_inputs(self) -> None:
        """
        Validate the required inputs. When the inputs are not valid, the action will fail.

        @return: None
        """
        if not self.github_token:
            logger.error("Failure: GITHUB_TOKEN is not set.")
            sys.exit(1)

        if not self.github_repository:
            logger.error("Failure: GITHUB_REPOSITORY is not set.")
            sys.exit(1)

        if len(self.version_tag_str) == 0:
            logger.error("Failure: VERSION_TAG is not set.")
            sys.exit(1)

        if len(self.branch) == 0:
            logger.error("Failure: BRANCH is not set.")
            sys.exit(1)
