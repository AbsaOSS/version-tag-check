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
This module contains the GitHubRepository class that is used to interact with the GitHub API.
"""
import requests

from requests import RequestException
from version_tag_check.version import Version


# pylint: disable=too-few-public-methods
class GitHubRepository:
    """
    A class that represents a GitHub repository and provides methods to interact
    """

    def __init__(self, owner: str, repo: str, token: str) -> None:
        """
        Initialize the GitHubRepository with the owner, repo and token.

        @param owner: The owner of the repository
        @param repo: The name of the repository
        @param token: The GitHub API token
        @return: None
        """
        self.owner = owner
        self.repo = repo
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github.v3+json"}

    def get_all_tags(self) -> list:
        """
        Get all tags for the repository.

        @return: A list of Version objects representing the tags
        """
        tags = []
        page = 1
        per_page = 100
        while True:
            response = requests.get(
                f"https://api.github.com/repos/{self.owner}/{self.repo}/tags",
                headers=self.headers,
                params={"per_page": per_page, "page": page},
                timeout=5,
            )
            if response.status_code != 200:
                raise RequestException(f"Failed to fetch tags: {response.status_code} {response.text}")
            page_tags = response.json()
            if not page_tags:
                break
            for tag_info in page_tags:
                tag_name = tag_info["name"]
                try:
                    version = Version(tag_name)
                    tags.append(version)
                except ValueError:
                    pass  # Ignore tags that are not valid versions
            if len(page_tags) < per_page:
                break
            page += 1
        return tags
