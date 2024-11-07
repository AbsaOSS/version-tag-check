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

import re
from functools import total_ordering


@total_ordering
class Version:
    """
    Class to represent a version and compare it to other versions.
    """

    VERSION_REGEX = r"^v(\d+)\.(\d+)\.(\d+)$"

    def __init__(self, version_str: str) -> None:
        """
        Initialize the Version with the version string.

        @param version_str: The version string in the format "vX.Y.Z"
        @return: None
        """
        self.version_str = version_str
        self.major = None
        self.minor = None
        self.patch = None
        self.parse()

    def parse(self) -> None:
        """
        Parse the version string into major, minor and patch components.

        @return: None
        """
        match = re.match(self.VERSION_REGEX, self.version_str)
        if not match:
            raise ValueError(f"Invalid version format: {self.version_str}")
        self.major, self.minor, self.patch = map(int, match.groups())

    def is_valid_format(self) -> bool:
        """
        Check if the version string is in the correct format.

        @return: True if the version string is in the correct format, False otherwise
        """
        return re.match(self.VERSION_REGEX, self.version_str) is not None

    def __eq__(self, other) -> bool:
        """
        Compare the Version to another Version.

        @param other: The other Version to compare to
        @return: True if the Versions are equal, False otherwise
        """
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other) -> bool:
        """
        Compare the Version to another Version.

        @param other: The other Version to compare to
        @return: True if the Version is less than the other Version, False otherwise
        """
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __str__(self) -> str:
        """
        Get the string representation of the Version.

        @return: The string representation of the Version
        """
        return self.version_str
