"""Integration-style tests that run the action via main.py for local execution.

These tests execute the action entrypoint (main.py) in a subprocess to cover the
real wiring (logging setup + VersionTagCheckAction).

To avoid real network calls, GitHubRepository is patched in the child process
via a temporary ``sitecustomize.py`` module.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from version_tag_check.utils.contansts import ERROR_TAG_ALREADY_EXISTS

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_local_run_successful_new_version(subprocess_env_with_mocked_github):
    """Run main.py as a subprocess and expect success for a valid new version.

    Scenario: New tag v0.1.1 is a valid patch increment on top of existing
    v0.1.0.
    """

    # Use the fixture to get the environment with mocked GitHubRepository
    env = subprocess_env_with_mocked_github

    # Provide action inputs via the same environment variables used in the action.yml
    env["INPUT_GITHUB_TOKEN"] = "fake-token"
    env["INPUT_GITHUB_REPOSITORY"] = "owner/repo"
    env["INPUT_VERSION_TAG"] = "v0.1.1"
    env["INPUT_SHOULD_EXIST"] = "false"

    # Enable debug logging so we can see integration-level logs if needed
    env["RUNNER_DEBUG"] = "1"

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py")],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


@pytest.mark.integration
def test_local_run_fails_on_existing_tag(subprocess_env_with_mocked_github):
    """Run main.py as a subprocess and expect failure when tag already exists.

    Scenario: New tag v0.1.0 already exists in the list returned by
    DummyGitHubRepository, so the action should fail.
    """

    env = subprocess_env_with_mocked_github

    env["INPUT_GITHUB_TOKEN"] = "fake-token"
    env["INPUT_GITHUB_REPOSITORY"] = "owner/repo"
    env["INPUT_VERSION_TAG"] = "v0.1.0"  # already present in DummyGitHubRepository
    env["INPUT_SHOULD_EXIST"] = "false"

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py")],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert ERROR_TAG_ALREADY_EXISTS in (result.stdout + result.stderr)
