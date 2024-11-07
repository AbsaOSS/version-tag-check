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

@pytest.fixture
def mock_logging_setup(mocker):
    """Fixture to mock the basic logging setup using pytest-mock."""
    mock_log_config = mocker.patch("logging.basicConfig")
    yield mock_log_config

@pytest.fixture()
def mock_exit(code) -> list:
    exit_calls = []
    exit_calls.append(code)
    return exit_calls
