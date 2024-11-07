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
This module contains the main script for the Version Tag Check GH Action.
"""

from typing import Optional

from version_tag_check.version import Version


class VersionValidator:
    """
    Class to validate the new version against the existing versions.
    """
    def __init__(self, new_version: Version, existing_versions: list) -> None:
        """
        Initialize the VersionValidator with the new version and existing versions.

        @param new_version: The new version to validate
        @param existing_versions: A list of existing versions to compare against
        @return: None
        """
        self.new_version = new_version
        self.existing_versions = existing_versions

    def get_latest_version(self) -> Optional[Version]:
        """
        Get the latest version from the existing versions.

        @return: The latest version or None if no versions exist
        """
        if not self.existing_versions:
            return None
        return max(self.existing_versions)

    def is_valid_increment(self) -> bool:
        """
        Check if the new version is a valid increment from the latest version.

        @return: True if the new version is a valid increment, False otherwise
        """
        latest_version = self.get_latest_version()
        if not latest_version:
            # Any version is valid if no previous versions exist
            return True

        lv = latest_version
        nv = self.new_version

        if nv.major == lv.major:
            if nv.minor == lv.minor:
                return nv.patch == lv.patch + 1
            elif nv.minor == lv.minor + 1:
                return nv.patch == 0
            else:
                return False
        elif nv.major == lv.major + 1:
            return nv.minor == 0 and nv.patch == 0
        else:
            return False
