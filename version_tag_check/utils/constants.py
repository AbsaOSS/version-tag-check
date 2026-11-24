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
This module contains the constants used in the version tag check action.
"""

# Error messages
ERROR_TAG_ALREADY_EXISTS = "The tag already exists in the repository."
ERROR_TAG_DOES_NOT_EXIST = "The tag does not exist in the repository."
ERROR_TAG_INVALID_FORMAT = (
    'Tag does not match the required format "v[0-9]+.[0-9]+.[0-9]+([-][A-Z0-9]+)?" '
    'or the PEP 440 release candidate form "v[0-9]+.[0-9]+.[0-9]+rc[1-9][0-9]?"'
)
