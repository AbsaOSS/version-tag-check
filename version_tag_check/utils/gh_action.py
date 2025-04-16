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
This module provides utilities for GitHub Actions.
"""
import logging
import os
import sys
from typing import Optional

logger = logging.getLogger(__name__)


def get_action_input(name: str, default: Optional[str] = None) -> str:
    """
    Retrieve the value of a specified input parameter from environment variables.

    @param name: The name of the input parameter.
    @param default: The default value to return if the environment variable is not set.

    @return: The value of the specified input parameter, or an empty string if the environment variable is not set.
    """
    return os.getenv(f'INPUT_{name.replace("-", "_").upper()}', default)    # type: ignore[arg-type]


def set_action_failed(message: str) -> None:
    """
    Mark the GitHub Action as failed and exit with an error message.

    @param message: The error message to be displayed.
    @return: None
    """
    logging.error(message)
    print(f"::error::{message}")
    sys.exit(1)
