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

from version_tag_check.version import Version


# is_valid_format

def test_is_valid_format_true():
    version = Version("v10.20.30")

    assert version.is_valid_format() is True

def test_is_valid_format_false():
    version = Version("v1.2")

    assert version.is_valid_format() is False


# __eq__

def test_equality_true():
    v1 = Version("v1.2.3")
    v2 = Version("v1.2.3")

    assert v1 == v2

def test_equality_false():
    v1 = Version("v1.2.3")
    v2 = Version("v1.2.4")

    assert not v1 == v2

def test_equality_not_valid():
    v1 = Version("x1.2.3")
    v2 = Version("v1.2.4")

    assert not v1 == v2

def test_equality_other_not_valid():
    v1 = Version("v1.2.3")
    v2 = Version("x1.2.4")

    assert not v1 == v2

def test_equality_other_is_none():
    v1 = Version("v1.2.3")

    assert not v1 == None


# __lt__

def test_less_than_true():
    v1 = Version("v1.2.3")
    v2 = Version("v1.2.4")

    assert v1 < v2

def test_less_than_false():
    v1 = Version("v2.0.0")
    v2 = Version("v1.9.9")

    assert not v1 < v2

def test_less_than_not_valid():
    v1 = Version("v2.0.0")
    v2 = Version("x1.9.9")

    assert not v2 < v1

def test_less_than_other_not_valid():
    v1 = Version("x2.0.0")
    v2 = Version("v1.9.9")

    assert not v2 < v1

def test_less_than_other_is_none():
    v = Version("v1.9.9")

    assert not v < None


# __gt__

def test_greater_than_true():
    v1 = Version("v1.2.3")
    v2 = Version("v1.2.4")

    assert v2 > v1

def test_greater_than_false():
    v1 = Version("v2.0.0")
    v2 = Version("v1.9.9")

    assert not v2 > v1

def test_greater_than_not_valid():
    v1 = Version("v2.0.0")
    v2 = Version("x1.9.9")

    assert not v1 > v2

def test_greater_than_other_not_valid():
    v1 = Version("x2.0.0")
    v2 = Version("v1.9.9")

    assert not v1 > v2

def test_greater_than_other_is_none():
    v = Version("v1.9.9")

    assert not v > None


# __str__

def test_str_representation_no_v_prefix():
    version_str = "1.2.3"
    version = Version(version_str)

    assert version.is_valid_format() == False
    assert str(version) == "vx.x.x"

def test_str_representation_v_prefix():
    version_str = "v1.2.3"
    version = Version(version_str)

    assert str(version) == version_str


# Qualifier parsing tests

def test_parse_version_without_qualifier():
    version = Version("v1.0.0")
    
    assert version.is_valid_format() is True
    assert version.major == 1
    assert version.minor == 0
    assert version.patch == 0
    assert version.qualifier is None
    assert str(version) == "v1.0.0"


def test_parse_version_with_snapshot():
    version = Version("v1.0.0-SNAPSHOT")
    
    assert version.is_valid_format() is True
    assert version.major == 1
    assert version.minor == 0
    assert version.patch == 0
    assert version.qualifier == "SNAPSHOT"
    assert str(version) == "v1.0.0-SNAPSHOT"


def test_parse_version_with_alpha():
    version = Version("v1.0.0-ALPHA")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "ALPHA"
    assert str(version) == "v1.0.0-ALPHA"


def test_parse_version_with_beta():
    version = Version("v1.0.0-BETA")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "BETA"
    assert str(version) == "v1.0.0-BETA"


def test_parse_version_with_rc1():
    version = Version("v1.0.0-RC1")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "RC1"
    assert str(version) == "v1.0.0-RC1"


def test_parse_version_with_rc10():
    version = Version("v1.0.0-RC10")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "RC10"
    assert str(version) == "v1.0.0-RC10"


def test_parse_version_with_release():
    version = Version("v1.0.0-RELEASE")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "RELEASE"
    assert str(version) == "v1.0.0-RELEASE"


def test_parse_version_with_hf1():
    version = Version("v1.0.0-HF1")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "HF1"
    assert str(version) == "v1.0.0-HF1"


def test_parse_version_with_hf10():
    version = Version("v1.0.0-HF10")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "HF10"
    assert str(version) == "v1.0.0-HF10"


def test_parse_version_with_lowercase_qualifier_invalid():
    version = Version("v1.0.0-snapshot")
    
    # The regex will reject lowercase qualifiers
    assert version.is_valid_format() is False


def test_parse_version_with_empty_qualifier_invalid():
    version = Version("v1.0.0-")
    
    # The regex requires at least one character after hyphen
    assert version.is_valid_format() is False


def test_parse_version_with_multiple_hyphens_invalid():
    version = Version("v1.0.0-RC1-SNAPSHOT")
    
    # The regex [A-Z0-9]+ doesn't match hyphens, so this will be invalid
    assert version.is_valid_format() is False


# Qualifier validation tests

def test_validate_qualifier_none():
    version = Version("v1.0.0")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_snapshot():
    version = Version("v1.0.0-SNAPSHOT")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_alpha():
    version = Version("v1.0.0-ALPHA")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_beta():
    version = Version("v1.0.0-BETA")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_release():
    version = Version("v1.0.0-RELEASE")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_rc1():
    version = Version("v1.0.0-RC1")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_rc2():
    version = Version("v1.0.0-RC2")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_rc99():
    version = Version("v1.0.0-RC99")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_hf1():
    version = Version("v1.0.0-HF1")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_hf2():
    version = Version("v1.0.0-HF2")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_hf99():
    version = Version("v1.0.0-HF99")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_lowercase_snapshot_invalid():
    version = Version("v1.0.0-snapshot")
    # This won't parse at all
    assert version.is_valid_format() is False


def test_validate_qualifier_lowercase_alpha_invalid():
    version = Version("v1.0.0-alpha")
    # This won't parse at all
    assert version.is_valid_format() is False


def test_validate_qualifier_lowercase_rc1_invalid():
    version = Version("v1.0.0-rc1")
    # This won't parse at all
    assert version.is_valid_format() is False


def test_validate_qualifier_lowercase_hf1_invalid():
    version = Version("v1.0.0-hf1")
    # This won't parse at all
    assert version.is_valid_format() is False


def test_validate_qualifier_rc_without_number_invalid():
    version = Version("v1.0.0-RC")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'RC'" in error
    assert "RC1-RC99" in error


def test_validate_qualifier_rc0_invalid():
    version = Version("v1.0.0-RC0")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'RC0'" in error


def test_validate_qualifier_rc001_invalid():
    version = Version("v1.0.0-RC001")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'RC001'" in error


def test_validate_qualifier_rc100_invalid():
    version = Version("v1.0.0-RC100")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'RC100'" in error


def test_validate_qualifier_hf_without_number_invalid():
    version = Version("v1.0.0-HF")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'HF'" in error
    assert "HF1-HF99" in error


def test_validate_qualifier_hf0_invalid():
    version = Version("v1.0.0-HF0")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'HF0'" in error


def test_validate_qualifier_hf001_invalid():
    version = Version("v1.0.0-HF001")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'HF001'" in error


def test_validate_qualifier_hf100_invalid():
    version = Version("v1.0.0-HF100")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'HF100'" in error


def test_validate_qualifier_snapshot1_invalid():
    version = Version("v1.0.0-SNAPSHOT1")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'SNAPSHOT1'" in error


def test_validate_qualifier_beta1_invalid():
    version = Version("v1.0.0-BETA1")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'BETA1'" in error


def test_validate_qualifier_unknown_invalid():
    version = Version("v1.0.0-UNKNOWN")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert "Invalid qualifier 'UNKNOWN'" in error
