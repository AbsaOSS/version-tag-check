"""Tests for repository tag discovery without network access."""

from unittest.mock import Mock

import pytest

from version_tag_check.github_repository import GitHubRepository
from version_tag_check.version import Version
from version_tag_check.version_validator import NewVersionValidator


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("new_tag", ["v1.0.1", "v1.1.0", "v2.0.0"])
def test_non_version_tags_do_not_block_increments(mocker, reverse, new_tag):
    names = ["latest", "stable", "v1", "1.0.0", "release-1.2", "v9.0.0-FOO", "v1.0.0"]
    if reverse:
        names.reverse()
    mocker.patch(
        "version_tag_check.github_repository.requests.get",
        return_value=Mock(status_code=200, json=Mock(return_value=[{"name": name} for name in names])),
    )

    tags = GitHubRepository("owner", "repo", "fake-token").get_all_tags()

    assert [str(tag) for tag in tags] == ["v1.0.0"]
    assert NewVersionValidator(Version(new_tag), tags).is_valid_increment()


def test_invalid_full_page_does_not_hide_later_versions(mocker):
    get = mocker.patch(
        "version_tag_check.github_repository.requests.get",
        side_effect=[
            Mock(status_code=200, json=Mock(return_value=[{"name": "latest"}] * 100)),
            Mock(status_code=200, json=Mock(return_value=[{"name": "v1.0.0-RC1"}, {"name": "v1.0.0"}])),
        ],
    )

    tags = GitHubRepository("owner", "repo", "fake-token").get_all_tags()

    assert [str(tag) for tag in tags] == ["v1.0.0-RC1", "v1.0.0"]
    assert [call.kwargs["params"]["page"] for call in get.call_args_list] == [1, 2]


def test_repository_with_only_invalid_tags_has_no_versions(mocker):
    mocker.patch(
        "version_tag_check.github_repository.requests.get",
        return_value=Mock(status_code=200, json=Mock(return_value=[{"name": "v9.0.0-HF0"}])),
    )

    tags = GitHubRepository("owner", "repo", "fake-token").get_all_tags()

    assert tags == []
    assert NewVersionValidator(Version("v1.0.0"), tags).is_valid_increment()
