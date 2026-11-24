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

import pytest

from version_tag_check.version import Version


# is_valid_format

def test_is_valid_format_true() -> None:
    version = Version("v10.20.30")

    assert version.is_valid_format() is True


def test_is_valid_format_false() -> None:
    version = Version("v1.2")

    assert version.is_valid_format() is False


# __eq__

def test_equality_true() -> None:
    v1 = Version("v1.2.3")
    v2 = Version("v1.2.3")

    assert v1 == v2


def test_equality_false() -> None:
    v1 = Version("v1.2.3")
    v2 = Version("v1.2.4")

    assert not v1 == v2


def test_equality_not_valid() -> None:
    v1 = Version("x1.2.3")
    v2 = Version("v1.2.4")

    assert not v1 == v2


def test_equality_other_not_valid() -> None:
    v1 = Version("v1.2.3")
    v2 = Version("x1.2.4")

    assert not v1 == v2


def test_equality_other_is_none() -> None:
    v1 = Version("v1.2.3")

    assert not v1 == None


# __lt__

def test_less_than_true() -> None:
    v1 = Version("v1.2.3")
    v2 = Version("v1.2.4")

    assert v1 < v2


def test_less_than_false() -> None:
    v1 = Version("v2.0.0")
    v2 = Version("v1.9.9")

    assert not v1 < v2


def test_less_than_not_valid() -> None:
    v1 = Version("v2.0.0")
    v2 = Version("x1.9.9")

    assert not v2 < v1


def test_less_than_other_not_valid() -> None:
    v1 = Version("x2.0.0")
    v2 = Version("v1.9.9")

    assert not v2 < v1


def test_less_than_other_is_none() -> None:
    v = Version("v1.9.9")

    assert not v < None


# __gt__

def test_greater_than_true() -> None:
    v1 = Version("v1.2.3")
    v2 = Version("v1.2.4")

    assert v2 > v1


def test_greater_than_false() -> None:
    v1 = Version("v2.0.0")
    v2 = Version("v1.9.9")

    assert not v2 > v1


def test_greater_than_not_valid() -> None:
    v1 = Version("v2.0.0")
    v2 = Version("x1.9.9")

    assert not v1 > v2


def test_greater_than_other_not_valid() -> None:
    v1 = Version("x2.0.0")
    v2 = Version("v1.9.9")

    assert not v1 > v2


def test_greater_than_other_is_none() -> None:
    v = Version("v1.9.9")

    assert not v > None


# __str__

def test_str_representation_no_v_prefix() -> None:
    version_str = "1.2.3"
    version = Version(version_str)

    assert version.is_valid_format() == False
    assert str(version) == "vx.x.x"


def test_str_representation_v_prefix() -> None:
    version_str = "v1.2.3"
    version = Version(version_str)

    assert str(version) == version_str


# Qualifier parsing tests

def test_parse_version_without_qualifier() -> None:
    version = Version("v1.0.0")
    
    assert version.is_valid_format() is True
    assert version.major == 1
    assert version.minor == 0
    assert version.patch == 0
    assert version.qualifier is None
    assert str(version) == "v1.0.0"


def test_parse_version_with_snapshot() -> None:
    version = Version("v1.0.0-SNAPSHOT")
    
    assert version.is_valid_format() is True
    assert version.major == 1
    assert version.minor == 0
    assert version.patch == 0
    assert version.qualifier == "SNAPSHOT"
    assert str(version) == "v1.0.0-SNAPSHOT"


def test_parse_version_with_alpha() -> None:
    version = Version("v1.0.0-ALPHA")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "ALPHA"
    assert str(version) == "v1.0.0-ALPHA"


def test_parse_version_with_beta() -> None:
    version = Version("v1.0.0-BETA")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "BETA"
    assert str(version) == "v1.0.0-BETA"


def test_parse_version_with_rc1() -> None:
    version = Version("v1.0.0-RC1")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "RC1"
    assert str(version) == "v1.0.0-RC1"


def test_parse_version_with_rc10() -> None:
    version = Version("v1.0.0-RC10")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "RC10"
    assert str(version) == "v1.0.0-RC10"


def test_parse_version_with_release() -> None:
    version = Version("v1.0.0-RELEASE")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "RELEASE"
    assert str(version) == "v1.0.0-RELEASE"


def test_parse_version_with_hf1() -> None:
    version = Version("v1.0.0-HF1")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "HF1"
    assert str(version) == "v1.0.0-HF1"


def test_parse_version_with_hf10() -> None:
    version = Version("v1.0.0-HF10")
    
    assert version.is_valid_format() is True
    assert version.qualifier == "HF10"
    assert str(version) == "v1.0.0-HF10"


def test_parse_version_with_lowercase_qualifier_invalid() -> None:
    version = Version("v1.0.0-snapshot")
    
    # The regex will reject lowercase qualifiers
    assert version.is_valid_format() is False


def test_parse_version_with_empty_qualifier_invalid() -> None:
    version = Version("v1.0.0-")
    
    # The regex requires at least one character after hyphen
    assert version.is_valid_format() is False


def test_parse_version_with_multiple_hyphens_invalid() -> None:
    version = Version("v1.0.0-RC1-SNAPSHOT")
    
    # The regex [A-Z0-9]+ doesn't match hyphens, so this will be invalid
    assert version.is_valid_format() is False


# Qualifier validation tests

def test_validate_qualifier_none() -> None:
    version = Version("v1.0.0")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_snapshot() -> None:
    version = Version("v1.0.0-SNAPSHOT")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_alpha() -> None:
    version = Version("v1.0.0-ALPHA")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_beta() -> None:
    version = Version("v1.0.0-BETA")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_release() -> None:
    version = Version("v1.0.0-RELEASE")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_rc1() -> None:
    version = Version("v1.0.0-RC1")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_rc2() -> None:
    version = Version("v1.0.0-RC2")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_rc99() -> None:
    version = Version("v1.0.0-RC99")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_hf1() -> None:
    version = Version("v1.0.0-HF1")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_hf2() -> None:
    version = Version("v1.0.0-HF2")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_hf99() -> None:
    version = Version("v1.0.0-HF99")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is True
    assert error is None


def test_validate_qualifier_lowercase_snapshot_invalid() -> None:
    version = Version("v1.0.0-snapshot")
    # This won't parse at all
    assert version.is_valid_format() is False


def test_validate_qualifier_lowercase_alpha_invalid() -> None:
    version = Version("v1.0.0-alpha")
    # This won't parse at all
    assert version.is_valid_format() is False


def test_validate_qualifier_lowercase_rc1_invalid() -> None:
    version = Version("v1.0.0-rc1")
    # This won't parse at all
    assert version.is_valid_format() is False


def test_validate_qualifier_lowercase_hf1_invalid() -> None:
    version = Version("v1.0.0-hf1")
    # This won't parse at all
    assert version.is_valid_format() is False


def test_validate_qualifier_rc_without_number_invalid() -> None:
    version = Version("v1.0.0-RC")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'RC'" in error
    assert "RC1-RC99" in error


def test_validate_qualifier_rc0_invalid() -> None:
    version = Version("v1.0.0-RC0")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'RC0'" in error


def test_validate_qualifier_rc001_invalid() -> None:
    version = Version("v1.0.0-RC001")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'RC001'" in error


def test_validate_qualifier_rc100_invalid() -> None:
    version = Version("v1.0.0-RC100")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'RC100'" in error


def test_validate_qualifier_hf_without_number_invalid() -> None:
    version = Version("v1.0.0-HF")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'HF'" in error
    assert "HF1-HF99" in error


def test_validate_qualifier_hf0_invalid() -> None:
    version = Version("v1.0.0-HF0")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'HF0'" in error


def test_validate_qualifier_hf001_invalid() -> None:
    version = Version("v1.0.0-HF001")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'HF001'" in error


def test_validate_qualifier_hf100_invalid() -> None:
    version = Version("v1.0.0-HF100")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'HF100'" in error


def test_validate_qualifier_snapshot1_invalid() -> None:
    version = Version("v1.0.0-SNAPSHOT1")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'SNAPSHOT1'" in error


def test_validate_qualifier_beta1_invalid() -> None:
    version = Version("v1.0.0-BETA1")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'BETA1'" in error


def test_validate_qualifier_unknown_invalid() -> None:
    version = Version("v1.0.0-UNKNOWN")
    is_valid, error = version.is_valid_qualifier()
    
    assert is_valid is False
    assert error is not None
    assert "Invalid qualifier 'UNKNOWN'" in error


# Qualifier comparison tests

def test_comparison_numeric_precedence_over_qualifier() -> None:
    """Test that numeric version takes precedence over qualifiers"""
    v1 = Version("v2.0.0-SNAPSHOT")
    v2 = Version("v1.9.9-RELEASE")
    
    assert v1 > v2
    assert v2 < v1
    assert not v1 == v2


def test_comparison_same_numeric_different_qualifiers() -> None:
    """Test qualifier precedence for same numeric version"""
    snapshot = Version("v1.0.0-SNAPSHOT")
    alpha = Version("v1.0.0-ALPHA")
    beta = Version("v1.0.0-BETA")
    rc1 = Version("v1.0.0-RC1")
    release = Version("v1.0.0-RELEASE")
    bare = Version("v1.0.0")
    hf1 = Version("v1.0.0-HF1")
    
    # Test SNAPSHOT < ALPHA < BETA
    assert snapshot < alpha < beta
    
    # Test BETA < RC1
    assert beta < rc1
    
    # Test RC1 < RELEASE
    assert rc1 < release
    
    # Test RELEASE < bare version
    assert release < bare
    
    # Test bare version < HF1
    assert bare < hf1


def test_comparison_rc_numeric_ordering() -> None:
    """Test that RC qualifiers are ordered numerically, not lexically"""
    rc1 = Version("v1.0.0-RC1")
    rc2 = Version("v1.0.0-RC2")
    rc10 = Version("v1.0.0-RC10")
    
    assert rc1 < rc2 < rc10
    assert rc10 > rc2 > rc1


def test_comparison_hf_numeric_ordering() -> None:
    """Test that HF qualifiers are ordered numerically, not lexically"""
    hf1 = Version("v1.0.0-HF1")
    hf2 = Version("v1.0.0-HF2")
    hf10 = Version("v1.0.0-HF10")
    
    assert hf1 < hf2 < hf10
    assert hf10 > hf2 > hf1


def test_comparison_hotfix_after_bare_version() -> None:
    """Test that hotfix versions come after the bare version"""
    bare = Version("v1.0.0")
    hf1 = Version("v1.0.0-HF1")
    hf2 = Version("v1.0.0-HF2")
    
    assert bare < hf1 < hf2


def test_comparison_full_progression() -> None:
    """Test the full qualifier progression from spec section 4.2"""
    versions = [
        Version("v1.0.0-SNAPSHOT"),
        Version("v1.0.0-ALPHA"),
        Version("v1.0.0-BETA"),
        Version("v1.0.0-RC1"),
        Version("v1.0.0-RC2"),
        Version("v1.0.0-RELEASE"),
        Version("v1.0.0"),
    ]
    
    # Verify each version is less than the next
    for i in range(len(versions) - 1):
        assert versions[i] < versions[i + 1], f"{versions[i]} should be < {versions[i + 1]}"


def test_comparison_with_hotfixes() -> None:
    """Test version progression including hotfixes"""
    versions = [
        Version("v1.0.0-RC1"),
        Version("v1.0.0-RELEASE"),
        Version("v1.0.0"),
        Version("v1.0.0-HF1"),
        Version("v1.0.0-HF2"),
    ]
    
    # Verify each version is less than the next
    for i in range(len(versions) - 1):
        assert versions[i] < versions[i + 1], f"{versions[i]} should be < {versions[i + 1]}"


def test_comparison_equality_with_qualifiers() -> None:
    """Test equality comparison with qualifiers"""
    v1 = Version("v1.0.0-SNAPSHOT")
    v2 = Version("v1.0.0-SNAPSHOT")
    v3 = Version("v1.0.0-ALPHA")
    
    assert v1 == v2
    assert not v1 == v3
    assert not v2 == v3


def test_comparison_equality_bare_versions() -> None:
    """Test that bare versions are still equal"""
    v1 = Version("v1.0.0")
    v2 = Version("v1.0.0")
    
    assert v1 == v2


def test_comparison_cross_version_with_qualifiers() -> None:
    """Test comparisons across different numeric versions with qualifiers"""
    v1 = Version("v1.0.0-ALPHA")
    v2 = Version("v1.0.0-BETA")
    v3 = Version("v1.0.0")
    v4 = Version("v1.1.0-SNAPSHOT")
    
    assert v1 < v2 < v3 < v4


def test_comparison_rc99_and_release() -> None:
    """Test boundary condition: RC99 < RELEASE"""
    rc99 = Version("v1.0.0-RC99")
    release = Version("v1.0.0-RELEASE")
    
    assert rc99 < release


def test_comparison_hf99_boundary() -> None:
    """Test boundary condition: HF99 is valid and compares correctly"""
    hf1 = Version("v1.0.0-HF1")
    hf99 = Version("v1.0.0-HF99")
    
    assert hf1 < hf99


# PEP 440 release candidate "vX.Y.ZrcN"

def test_parse_pep440_rc1() -> None:
    version = Version("v0.9.0rc1")

    assert version.is_valid_format() is True
    assert version.major == 0
    assert version.minor == 9
    assert version.patch == 0
    assert version.qualifier == "RC1"
    assert str(version) == "v0.9.0rc1"


def test_parse_pep440_rc99() -> None:
    version = Version("v0.9.0rc99")

    assert version.is_valid_format() is True
    assert version.qualifier == "RC99"
    assert str(version) == "v0.9.0rc99"


def test_validate_qualifier_pep440_rc() -> None:
    version = Version("v0.9.0rc1")
    is_valid, error = version.is_valid_qualifier()

    assert is_valid is True
    assert error is None


@pytest.mark.parametrize(
    "version_str",
    [
        "v0.9.0rc0",       # rc0 left out, as RC0
        "v0.9.0rc100",     # above rc99
        "v0.9.0rc01",      # PEP 440 normalises away the leading zero
        "v0.9.0rc",        # number required
        "v0.9.0-rc1",      # hyphen not in the normalised spelling
        "v0.9.0.rc1",      # dot not in the normalised spelling
        "v0.9.0_rc1",      # underscore not in the normalised spelling
        "v0.9.0RC1",       # uppercase not in the normalised spelling
        "v0.9.0Rc1",       # mixed case not in the normalised spelling
        "v0.9.0c1",        # PEP 440 alternative spelling of rc
        "v0.9.0pre1",      # PEP 440 alternative spelling of rc
        "v0.9.0a1",        # PEP 440 alpha not supported
        "v0.9.0b1",        # PEP 440 beta not supported
        "v0.9.0rc1.post1",  # PEP 440 post-release not supported
        "v0.9.0rc1.dev1",  # PEP 440 development release not supported
        "v0.9.0rc1+local",  # PEP 440 local version not supported
        "v0.9.0rc1-SNAPSHOT",  # combined qualifiers
        "v0.9.0-RC1rc1",   # combined spellings
        "0.9.0rc1",        # v prefix required
    ],
)
def test_parse_pep440_rc_invalid(version_str: str) -> None:
    version = Version(version_str)

    assert version.is_valid_format() is False


def test_pep440_rc_equals_hyphen_rc() -> None:
    assert Version("v0.9.0rc1") == Version("v0.9.0-RC1")
    assert Version("v0.9.0-RC1") == Version("v0.9.0rc1")
    assert not Version("v0.9.0rc1") == Version("v0.9.0-RC2")
    assert not Version("v0.9.0rc1") < Version("v0.9.0-RC1")
    assert not Version("v0.9.0rc1") > Version("v0.9.0-RC1")


def test_str_keeps_spelling_of_each_rc_form() -> None:
    assert str(Version("v0.9.0rc1")) == "v0.9.0rc1"
    assert str(Version("v0.9.0-RC1")) == "v0.9.0-RC1"


def test_comparison_pep440_rc_progression() -> None:
    versions = [
        Version("v0.8.1"),
        Version("v0.9.0-BETA"),
        Version("v0.9.0rc1"),
        Version("v0.9.0rc2"),
        Version("v0.9.0rc10"),
        Version("v0.9.0-RELEASE"),
        Version("v0.9.0"),
        Version("v0.9.0-HF1"),
    ]

    for i in range(len(versions) - 1):
        assert versions[i] < versions[i + 1], f"{versions[i]} should be < {versions[i + 1]}"
        assert versions[i + 1] > versions[i], f"{versions[i + 1]} should be > {versions[i]}"


def test_comparison_mixed_rc_history() -> None:
    history = [Version("v0.9.0rc3"), Version("v0.9.0-RC1"), Version("v0.9.0rc2"), Version("v0.8.1")]

    assert [str(v) for v in sorted(history)] == ["v0.8.1", "v0.9.0-RC1", "v0.9.0rc2", "v0.9.0rc3"]
    assert str(max(history)) == "v0.9.0rc3"


def test_custom_regex_without_pep440_group_keeps_its_qualifier() -> None:
    version = Version("v1.0.0-X+7", version_regex=r"^v(\d+)\.(\d+)\.(\d+)-([A-Z])\+(\d+)$")

    assert version.is_valid_format() is True
    assert version.qualifier == "X"
    assert str(version) == "v1.0.0-X"
