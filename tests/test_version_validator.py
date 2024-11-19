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


# is_valid_increment

import pytest

from version_tag_check.version import Version
from version_tag_check.version_validator import NewVersionValidator

# Test cases in the format: (existing_versions, new_version, expected_result)
test_cases = [
    ([], "v1.0.0", True),  # No existing versions; any version is valid
    (["v1.0.0"], "v1.0.1", True),  # Patch increment
    (["v1.0.1"], "v1.1.0", True),  # Minor increment with zero patch
    (["v1.1.0"], "v1.2.0", True),  # Minor increment with zero patch
    (["v1.1.0"], "v2.0.0", True),  # Major increment with zero minor and patch
    (["v1.1.1"], "v1.2.0", True),  # Minor increment with zero patch
    (["v1.1.1"], "v2.0.0", True),  # Major increment with zero minor and patch
    (["v1.1.1"], "v1.1.3", False),  # Invalid patch increment (skipping patch version)
    (["v1.1.1"], "v1.2.1", False),  # Invalid minor increment with non-zero patch
    (["v1.1.1"], "v2.1.0", False),  # Invalid major increment with non-zero minor
    (["v1.1.1"], "v1.0.2", False),  # New version less than latest
    (["v1.1.1"], "v1.1.1", False),  # New version equal to latest
    (["v1.0.0", "v1.0.1", "v1.1.0", "v1.1.1"], "v1.1.2", True),  # Multiple existing versions
    (["v1.1.1"], "v3.0.0", False),  # Skipping major version
    (["v1.1.1"], "v1.3.0", False),  # Skipping minor version
    (["v1.1.1"], "v1.1.3", False),  # Skipping patch version
]

@pytest.mark.parametrize("existing_versions_str, new_version_str, expected", test_cases)
def test_is_valid_increment(existing_versions_str, new_version_str, expected):
    existing_versions = [Version(v_str) for v_str in existing_versions_str]
    new_version = Version(new_version_str)
    validator = NewVersionValidator(new_version, existing_versions)

    assert validator.is_valid_increment() == expected
