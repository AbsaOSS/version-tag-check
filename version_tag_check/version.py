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
            # groups[3] is the optional qualifier group; it's None if not matched
            self.__qualifier = groups[3] if len(groups) > 3 and groups[3] is not None else None
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
        for pattern in qualifier_patterns.values():
            if re.match(pattern, self.__qualifier):
                return True, None

        # If no pattern matched, generate a helpful error message
        error_msg = f"Invalid qualifier '{self.__qualifier}'. "
        error_msg += "Allowed qualifiers are: SNAPSHOT, ALPHA, BETA, RC1-RC99, RELEASE, HF1-HF99"
        return False, error_msg

    def _get_qualifier_precedence(self) -> tuple[int, int]:  # pylint: disable=too-many-return-statements
        """
        Get the precedence value for the qualifier.

        Returns a tuple (category, number) where:
        - category: the precedence category (0-6)
        - number: the numeric suffix for RC and HF qualifiers (0 otherwise)

        Precedence order:
        0: SNAPSHOT (lowest)
        1: ALPHA
        2: BETA
        3: RC1-RC99
        4: RELEASE
        5: No qualifier (bare version)
        6: HF1-HF99 (highest)

        @return: A tuple of (category, number)
        """
        if self.__qualifier is None:
            return (5, 0)  # No qualifier - between RELEASE and HF

        if self.__qualifier == "SNAPSHOT":
            return (0, 0)
        if self.__qualifier == "ALPHA":
            return (1, 0)
        if self.__qualifier == "BETA":
            return (2, 0)
        if self.__qualifier == "RELEASE":
            return (4, 0)

        # Handle RC with numeric suffix
        rc_match = re.match(r"^RC(\d+)$", self.__qualifier)
        if rc_match:
            return (3, int(rc_match.group(1)))

        # Handle HF with numeric suffix
        hf_match = re.match(r"^HF(\d+)$", self.__qualifier)
        if hf_match:
            return (6, int(hf_match.group(1)))

        # Invalid qualifier - return lowest precedence
        return (-1, 0)

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

        # Compare numeric components first
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return False

        # If numeric components are equal, compare qualifiers
        return self._get_qualifier_precedence() == other._get_qualifier_precedence()  # pylint: disable=protected-access

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

        # Compare numeric components first
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

        # If numeric components are equal, compare qualifiers
        return self._get_qualifier_precedence() < other._get_qualifier_precedence()  # pylint: disable=protected-access

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

        # Compare numeric components first
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

        # If numeric components are equal, compare qualifiers
        return self._get_qualifier_precedence() > other._get_qualifier_precedence()  # pylint: disable=protected-access

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
