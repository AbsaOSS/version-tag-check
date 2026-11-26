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

import os
from collections.abc import Iterator

import pytest
from pytest_mock import MockerFixture, MockType


@pytest.fixture(autouse=True)
def clean_action_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fixture to start every unit test without RUNNER_DEBUG or any INPUT_* action input, whatever the runner sets."""
    monkeypatch.delenv("RUNNER_DEBUG", raising=False)
    for name in [name for name in os.environ if name.startswith("INPUT_")]:
        monkeypatch.delenv(name)


@pytest.fixture
def mock_logging_setup(mocker: MockerFixture) -> Iterator[MockType]:
    """Fixture to mock the basic logging setup using pytest-mock."""
    mock_log_config = mocker.patch("logging.basicConfig")
    yield mock_log_config
