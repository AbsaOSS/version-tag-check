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

    VERSION_REGEX = r"^v(\d+)\.(\d+)\.(\d+)(?:-([A-Z0-9]+))?$"

    def __init__(self, version_str: str, version_regex: str = VERSION_REGEX) -> None:
        """
        Initialize the Version with the version string.

        @param version_str: The version string in the format "vX.Y.Z" or "vX.Y.Z-QUALIFIER"
        @return: None
        """
        self.__version_regex = version_regex

        self.__major: Optional[int] = None
        self.__minor: Optional[int] = None
        self.__patch: Optional[int] = None
        self.__qualifier: Optional[str] = None
        self.__valid: Optional[bool] = None

        self.__parse(version_str)

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

    @property
    def qualifier(self) -> Optional[str]:
        """
        Get the qualifier.

        @return: The qualifier string, or None if no qualifier is present
        """
        return self.__qualifier

    def __parse(self, version_str: str) -> None:
        """
        Parse the version string into major, minor, patch, and optional qualifier.

        @return: None
        """
        match = re.match(self.__version_regex, version_str)
        if match:
            groups = match.groups()
            self.__major, self.__minor, self.__patch = map(int, groups[:3])
            self.__qualifier = groups[3] if len(groups) > 3 else None
            self.__valid = True
            logger.info("Version '%s' parsed successfully.", version_str)
        else:
            self.__valid = False
            logger.error("Version '%s' does not match the required format.", version_str)

    def is_valid_format(self) -> bool:
        """
        Check if the version string is in the correct format.

        @return: True if the version string is in the correct format, False otherwise
        """
        return self.__valid if self.__valid is not None else False

    def is_valid_qualifier(self) -> tuple[bool, Optional[str]]:
        """
        Validate if the qualifier matches allowed patterns.

        @return: A tuple of (is_valid, error_message)
        """
        if self.__qualifier is None:
            return True, None

        # Allowed qualifier patterns
        qualifier_patterns = {
            "SNAPSHOT": r"^SNAPSHOT$",
            "ALPHA": r"^ALPHA$",
            "BETA": r"^BETA$",
            "RC": r"^RC([1-9][0-9]?)$",  # RC1 to RC99
            "RELEASE": r"^RELEASE$",
            "HF": r"^HF([1-9][0-9]?)$",  # HF1 to HF99
        }

        # Check each pattern
        for pattern_name, pattern in qualifier_patterns.items():
            if re.match(pattern, self.__qualifier):
                return True, None

        # If no pattern matched, generate a helpful error message
        error_msg = f"Invalid qualifier '{self.__qualifier}'. "
        error_msg += "Allowed qualifiers are: SNAPSHOT, ALPHA, BETA, RC1-RC99, RELEASE, HF1-HF99"
        return False, error_msg

    def __eq__(self, other) -> bool:
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

    def __str__(self) -> str:
        """
        Get the string representation of the Version.

        @return: The string representation of the Version
        """
        placeholder = "x"

        major = self.major if self.major is not None else placeholder
        minor = self.minor if self.minor is not None else placeholder
        patch = self.patch if self.patch is not None else placeholder
        base = f"v{major}.{minor}.{patch}"
        
        if self.qualifier is not None:
            return f"{base}-{self.qualifier}"
        return base
