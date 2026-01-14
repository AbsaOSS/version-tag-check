"""Test-only dummy GitHubRepository used by integration tests."""

from __future__ import annotations

from version_tag_check.version import Version


class DummyGitHubRepository:
    """Simple stand-in for GitHubRepository used in integration tests."""

    def __init__(self, owner: str, repo: str, token: str) -> None:
        self.owner = owner
        self.repo = repo
        self.token = token

    def get_all_tags(self) -> list[Version]:
        """Return a deterministic list of tags for integration tests."""

        return [Version("v0.0.1"), Version("v0.0.2"), Version("v0.1.0")]
