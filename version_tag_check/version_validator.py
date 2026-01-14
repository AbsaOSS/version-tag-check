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
import logging
from typing import Optional

from version_tag_check.version import Version

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class NewVersionValidator:
    """
    Class to validate the new version against the existing versions.
    """

    def __init__(self, new_version: Version, existing_versions: list[Version]) -> None:
        """
        Initialize the VersionValidator with the new version and existing versions.

        @param new_version: The new version to validate
        @param existing_versions: A list of existing versions to compare against
        @return: None
        """
        self.__new_version: Version = new_version
        self.__existing_versions: list[Version] = existing_versions

    def __get_latest_version(self) -> Optional[Version]:
        """
        Get the latest version from the existing versions.

        @return: The latest version or None if no versions exist
        """
        if not self.__existing_versions:
            return None
        return max(self.__existing_versions)

    def __get_filtered_versions(self, major: Optional[int], minor: Optional[int] = None) -> list[Version]:
        """
        Filter the existing versions based on major and optionally minor versions.

        @param major: The major version to filter by
        @param minor: The minor version to filter by (optional)
        @return: A list of versions matching the criteria
        """
        return [
            version
            for version in self.__existing_versions
            if (major is None or version.major == major) and (minor is None or version.minor == minor)
        ]

    def is_valid_increment(self) -> bool:  # pylint: disable=too-many-return-statements
        """
        Check if the new version is a valid increment from the latest version.

        Supports:
        - Qualifier progression within same numeric version
        - Version bumps (major, minor, patch) with or without qualifiers
        - Hotfix sequences after release
        - Backport patches to older version series

        @return: True if the new version is a valid increment, False otherwise
        """
        # check if the new version is the first version
        latest_version: Optional[Version] = self.__get_latest_version()
        logger.debug("Validator: Latest version: %s", latest_version)
        if not latest_version:
            # Any version is valid if no previous versions exist
            logger.info("No previous versions exist. New version is valid.")
            return True

        nv: Version = self.__new_version

        # If it's the same numeric version as latest, check qualifier progression
        if (nv.major, nv.minor, nv.patch) == (latest_version.major, latest_version.minor, latest_version.patch):
            if nv > latest_version:
                logger.info("Valid qualifier progression: %s -> %s", latest_version, nv)
                return True
            logger.error("New tag %s is not greater than the latest tag %s.", nv, latest_version)
            return False

        # For different numeric versions, check standard increment rules
        # Filter versions matching the major and minor version of the new version
        filtered_versions = self.__get_filtered_versions(nv.major, nv.minor)
        if len(filtered_versions) > 0:
            latest_filtered_version = max(filtered_versions)
            logger.debug("Validator: Latest filtered version: %s", latest_filtered_version)

            # Validate against the latest filtered version
            if nv.major == latest_filtered_version.major and nv.minor == latest_filtered_version.minor:
                if nv.patch == (latest_filtered_version.patch if latest_filtered_version.patch else 0) + 1:
                    logger.info("Valid patch increment: %s -> %s", latest_filtered_version, nv)
                    return True
                logger.error("New tag %s is not one patch higher than the latest tag %s.", nv, latest_filtered_version)
                # Don't return False here - continue to check if it's a valid minor/major bump

        # Check if this is a valid minor or major bump (only if greater than latest)
        if nv > latest_version:
            if nv.major == latest_version.major:
                if nv.minor == (latest_version.minor if latest_version.minor else 0) + 1:
                    if nv.patch == 0:
                        logger.info("Valid minor increment: %s -> %s", latest_version, nv)
                        return True
                    logger.error("New tag %s is not a valid minor bump. Latest version: %s.", nv, latest_version)
                    return False
            elif nv.major == (latest_version.major if latest_version.major else 0) + 1:
                if nv.minor == 0 and nv.patch == 0:
                    logger.info("Valid major increment: %s -> %s", latest_version, nv)
                    return True
                logger.error("New tag %s is not a valid major bump. Latest version: %s.", nv, latest_version)
                return False

        # If new version is not greater than latest and doesn't fit other patterns, it's invalid
        logger.error("New tag %s is not greater than the latest tag %s.", nv, latest_version)
        return False
