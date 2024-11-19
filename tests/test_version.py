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

def test_str_representation():
    version_str = "1.2.3"
    version = Version(version_str)

    assert str(version) == version_str
