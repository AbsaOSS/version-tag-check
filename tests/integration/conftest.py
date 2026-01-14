"""Shared fixtures and helpers for integration tests."""

import os
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def subprocess_env_with_mocked_github(tmp_path):
    """Create a subprocess environment with mocked GitHubRepository.
    
    This fixture prepares:
    - A copy of os.environ with PYTHONPATH pointing to the project root
    - A temporary sitecustomize.py module that patches GitHubRepository
      with DummyGitHubRepository before main.py runs
    
    The sitecustomize.py is auto-imported by Python at startup, ensuring
    the mock is applied before any production code executes.
    
    Returns:
        dict: Environment variables ready for subprocess.run(env=...)
    """
    # Base environment with PYTHONPATH including project root
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"
    
    # Create sitecustomize.py to patch GitHubRepository in the child process
    sitecustomize_path = tmp_path / "sitecustomize.py"
    sitecustomize_path.write_text(
        "from version_tag_check import github_repository as ghr\n"
        "from tests.integration.dummy_github_repository import DummyGitHubRepository\n"
        "ghr.GitHubRepository = DummyGitHubRepository\n",
        encoding="utf-8",
    )
    
    # Prepend temp directory so Python auto-imports our sitecustomize module
    env["PYTHONPATH"] = f"{tmp_path}{os.pathsep}{env['PYTHONPATH']}"
    
    return env
