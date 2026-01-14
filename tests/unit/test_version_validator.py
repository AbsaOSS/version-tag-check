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


# Test cases for qualifier progression
qualifier_test_cases = [
    # Valid qualifier progressions within same numeric version
    (["v1.0.0-SNAPSHOT"], "v1.0.0-ALPHA", True),
    (["v1.0.0-ALPHA"], "v1.0.0-BETA", True),
    (["v1.0.0-BETA"], "v1.0.0-RC1", True),
    (["v1.0.0-RC1"], "v1.0.0-RC2", True),
    (["v1.0.0-RC2"], "v1.0.0-RELEASE", True),
    (["v1.0.0-RELEASE"], "v1.0.0", True),
    (["v1.0.0"], "v1.0.0-HF1", True),
    (["v1.0.0-HF1"], "v1.0.0-HF2", True),
    
    # Invalid backwards qualifier progressions
    (["v1.0.0-RC2"], "v1.0.0-RC1", False),
    (["v1.0.0-ALPHA"], "v1.0.0-SNAPSHOT", False),
    (["v1.0.0"], "v1.0.0-RELEASE", False),
    (["v1.0.0-HF2"], "v1.0.0-HF1", False),
    
    # Cross-version transitions with qualifiers
    (["v1.0.0"], "v1.0.1-SNAPSHOT", True),
    (["v1.0.0"], "v1.1.0-SNAPSHOT", True),
    (["v1.0.0"], "v2.0.0-SNAPSHOT", True),
    (["v1.0.0-RELEASE"], "v1.0.1-SNAPSHOT", True),
    
    # Valid patch increment with qualifier reset
    (["v1.0.0"], "v1.0.1-ALPHA", True),
    (["v1.0.0-RELEASE"], "v1.0.1-BETA", True),
    
    # Full progression from spec examples
    (["v1.0.0-SNAPSHOT"], "v1.0.0-ALPHA", True),
    (["v1.0.0-SNAPSHOT", "v1.0.0-ALPHA"], "v1.0.0-BETA", True),
    (["v1.0.0-SNAPSHOT", "v1.0.0-ALPHA", "v1.0.0-BETA"], "v1.0.0-RC1", True),
    (["v1.0.0-SNAPSHOT", "v1.0.0-ALPHA", "v1.0.0-BETA", "v1.0.0-RC1"], "v1.0.0-RC2", True),
    (["v1.0.0-RC2"], "v1.0.0-RELEASE", True),
    (["v1.0.0-RELEASE"], "v1.0.0", True),
    
    # Hotfix sequence
    (["v1.0.0-RELEASE", "v1.0.0"], "v1.0.1", True),
    (["v1.0.0", "v1.0.1"], "v1.0.1-HF1", True),
    (["v1.0.0", "v1.0.1", "v1.0.1-HF1"], "v1.0.1-HF2", True),
    
    # Invalid: skipping qualifiers is still allowed (as long as it increases)
    (["v1.0.0-SNAPSHOT"], "v1.0.0-RC1", True),  # Valid: RC1 > SNAPSHOT
    (["v1.0.0-ALPHA"], "v1.0.0", True),  # Valid: bare > ALPHA
    
    # Numeric precedence over qualifiers
    (["v1.0.0-ALPHA"], "v1.0.1-SNAPSHOT", True),  # v1.0.1 > v1.0.0 regardless of qualifiers
    
    # RC ordering
    (["v1.0.0-RC1"], "v1.0.0-RC10", True),  # RC10 > RC1 (numeric comparison)
    (["v1.0.0-RC10"], "v1.0.0-RC2", False),  # RC2 < RC10
    
    # HF ordering  
    (["v1.0.0-HF1"], "v1.0.0-HF10", True),  # HF10 > HF1 (numeric comparison)
    (["v1.0.0-HF10"], "v1.0.0-HF2", False),  # HF2 < HF10
]

@pytest.mark.parametrize("existing_versions_str, new_version_str, expected", qualifier_test_cases)
def test_is_valid_increment_with_qualifiers(existing_versions_str, new_version_str, expected):
    existing_versions = [Version(v_str) for v_str in existing_versions_str]
    new_version = Version(new_version_str)
    validator = NewVersionValidator(new_version, existing_versions)

    assert validator.is_valid_increment() == expected
