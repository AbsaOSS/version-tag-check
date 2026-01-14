"""Integration-style tests that run the action via main.py for local execution.

These tests run the full wiring (logging setup + VersionTagCheckAction) but mock
GitHubRepository to avoid real network calls.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_local_run_successful_new_version(tmp_path):
    """Run main.py as a subprocess and expect success for a valid new version.

    Scenario: New tag v0.1.1 is a valid patch increment on top of existing
    v0.1.0.
    """

    # Ensure we import the project from the repo root when running via subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"

    # Provide action inputs via the same environment variables used in the action.yml
    env["INPUT_GITHUB_TOKEN"] = "fake-token"
    env["INPUT_GITHUB_REPOSITORY"] = "owner/repo"
    env["INPUT_VERSION_TAG"] = "v0.1.1"
    env["INPUT_SHOULD_EXIST"] = "false"

    # Enable debug logging so we can see integration-level logs if needed
    env["RUNNER_DEBUG"] = "1"

    # Monkeypatch GitHubRepository in the child process via sitecustomize.
    # We create a small sitecustomize module on the fly that patches the class
    # before main.py runs.
    sitecustomize_path = tmp_path / "sitecustomize.py"
    sitecustomize_path.write_text(
        "from version_tag_check import github_repository as ghr\n"
        "from tests.integration.dummy_github_repository import DummyGitHubRepository\n"
        "ghr.GitHubRepository = DummyGitHubRepository\n",
        encoding="utf-8",
    )

    env["PYTHONPATH"] = f"{tmp_path}{os.pathsep}{env['PYTHONPATH']}"

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py")],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


@pytest.mark.integration
def test_local_run_fails_on_existing_tag(tmp_path):
    """Run main.py as a subprocess and expect failure when tag already exists.

    Scenario: New tag v0.1.0 already exists in the list returned by
    DummyGitHubRepository, so the action should fail.
    """

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"

    env["INPUT_GITHUB_TOKEN"] = "fake-token"
    env["INPUT_GITHUB_REPOSITORY"] = "owner/repo"
    env["INPUT_VERSION_TAG"] = "v0.1.0"  # already present in DummyGitHubRepository
    env["INPUT_SHOULD_EXIST"] = "false"

    sitecustomize_path = tmp_path / "sitecustomize.py"
    sitecustomize_path.write_text(
        "from version_tag_check import github_repository as ghr\n"
        "from tests.integration.dummy_github_repository import DummyGitHubRepository\n"
        "ghr.GitHubRepository = DummyGitHubRepository\n",
        encoding="utf-8",
    )

    env["PYTHONPATH"] = f"{tmp_path}{os.pathsep}{env['PYTHONPATH']}"

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py")],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "The tag already exists in the repository" in (result.stdout + result.stderr)
