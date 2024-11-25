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
import re
from functools import total_ordering
from typing import Optional

logger = logging.getLogger(__name__)


@total_ordering
class Version:
    """
    Class to represent a version and compare it to other versions.
    """

    VERSION_REGEX = r"^v(\d+)\.(\d+)\.(\d+)$"

    def __init__(self, version_str: str, version_regex: str = VERSION_REGEX) -> None:
        """
        Initialize the Version with the version string.

        @param version_str: The version string in the format "vX.Y.Z"
        @return: None
        """
        self.__version_str = version_str
        self.__version_regex = version_regex

        self.__major = None
        self.__minor = None
        self.__patch = None
        self.__valid = None

        self.__parse()

    @property
    def major(self) -> Optional[int]:
        """
        Get the major version.

        @return: The major version
        """
        return self.__major

    @property
    def minor(self) -> Optional[int]:
        """
        Get the minor version.

        @return: The minor version
        """
        return self.__minor

    @property
    def patch(self) -> Optional[int]:
        """
        Get the patch version.

        @return: The patch version
        """
        return self.__patch

    def __parse(self) -> None:
        """
        Parse the version string into major, minor and patch.

        @return: None
        """
        match = re.match(self.__version_regex, self.__version_str)
        if match:
            self.__major, self.__minor, self.__patch = map(int, match.groups())
            self.__valid = True
            logger.info("Version '%s' parsed successfully.", self.__version_str)
        else:
            self.__valid = False
            logger.error("Version '%s' does not match the required format.", self.__version_str)

    def is_valid_format(self) -> bool:
        """
        Check if the version string is in the correct format.

        @return: True if the version string is in the correct format, False otherwise
        """
        return self.__valid

    def __eq__(self, other) -> Optional[bool]:
        """
        Compare the Version to another Version.

        @param other: The other Version to compare to
        @return: True if the Versions are equal, False otherwise
        """
        if other is None:
            return False

        if not self.is_valid_format() or not other.is_valid_format():
            return False

        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other) -> Optional[bool]:
        """
        Compare the Version to another Version.

        @param other: The other Version to compare to
        @return: True if the Version is less than the other Version, False otherwise
        """
        if other is None:
            return False

        if not self.is_valid_format() or not other.is_valid_format():
            return False

        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __gt__(self, other):
        """
        Compare the Version to another Version.

        @param other: The other Version to compare to
        @return: True if the Version is greater than the other Version, False otherwise
        """
        if other is None:
            return False

        if not self.is_valid_format() or not other.is_valid_format():
            return False

        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __str__(self) -> Optional[str]:
        """
        Get the string representation of the Version.

        @return: The string representation of the Version
        """
        return self.__version_str
