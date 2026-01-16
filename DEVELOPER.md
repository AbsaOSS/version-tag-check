# Version Tag Checker Developer Guide

- [Project Setup](#project-setup)
- [Run Scripts Locally](#run-scripts-locally)
- [Run Pylint Check Locally](#run-pylint-check-locally)
- [Run Black Tool Locally](#run-black-tool-locally)
- [Run mypy Tool Locally](#run-mypy-tool-locally)
- [Run Unit Tests with Pytest](#run-unit-tests-with-pytest)
- [Run Integration Tests with Pytest](#run-integration-tests-with-pytest)
- [Code Coverage with pytest-cov](#code-coverage-with-pytest-cov)
- [Releasing](#releasing)
- [Development Flow with GitHub Copilot](#development-flow-with-github-copilot)

## Project Setup

If you need to build the action locally, follow these steps for project setup:

### Prepare the Environment

```shell
python3 --version
```

### Set Up Python Environment

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---
## Run Scripts Locally

Create a `run_local.sh` file and place it in the project root. 

```bash
#!/bin/bash

# Ensure that Python virtual environment is activated
if [ ! -d ".venv" ]; then
  echo "Python virtual environment not found. Creating one..."
  python3 -m venv .venv
fi

source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN environment variable is not set."
  exit 1
fi

# Set necessary environment variables
export INPUT_GITHUB_TOKEN="$GITHUB_TOKEN"
export INPUT_VERSION_TAG="v1.2.3"
export INPUT_GITHUB_REPOSITORY="AbsaOSS/version-tag-check"

# Run the main script
python main.py
```

### Make the script executable

To avoid permission errors, make sure to give the script execute permissions:

```bash
chmod +x run_local.sh
```

Now you can run the script anytime with:

```bash
./run_local.sh
```

---
## Run Pylint Check Locally

This project uses the [Pylint](https://pypi.org/project/pylint/) tool for static code analysis.
Pylint analyses your code without actually running it.
It checks for errors, enforces coding standards, looks for code smells, etc.
We do exclude the `tests/` file from the Pylint check.

Pylint displays a global evaluation score for the code, rated out of a maximum score of 10.0.
We aim to keep our Pylint score above 9.5.

Follow these steps to run Pylint check locally:

- Perform the [setup of python venv](#set-up-python-environment).

### Run Pylint

Run Pylint on all files that are currently tracked by Git in the project.
```shell
pylint --ignore=tests $(git ls-files '*.py')
```

To run Pylint on a specific file, follow the pattern `pylint <path_to_file>/<name_of_file>.py`.

Example:
```shell
pylint ./version_tag_check/version_tag_check_action.py
``` 

### Expected Output

This is an example of the expected console output after running the tool:
```console
************* Module main
main.py:30:0: C0116: Missing function or method docstring (missing-function-docstring)

------------------------------------------------------------------
Your code has been rated at 9.41/10 (previous run: 8.82/10, +0.59)
```

---
## Run Black Tool Locally

This project uses the [Black](https://github.com/psf/black) tool for code formatting.
Black aims for consistency, generality, readability and reducing git diffs.
The coding style used can be viewed as a strict subset of PEP 8.

The `pyproject.toml` file defines the Black configuration.
In this project, we enforce a maximum line length of 120 characters.
We also exclude the `tests/` directory from formatting.

Follow these steps to format your code with Black locally:

- Perform the [setup of python venv](#set-up-python-environment).

### Run Black

Run Black on all files that are currently tracked by Git in the project.
```shell
black --exclude tests $(git ls-files '*.py')
```

To run Black on a specific file, follow the pattern `black <path_to_file>/<name_of_file>.py`.

Example:
```shell
black ./version_tag_check/version_tag_check_action.py
``` 

### Expected Output

This is an example of the expected console output after running the tool:
```console
All done! ✨ 🍰 ✨
1 file reformatted.
```

---

## Run mypy Tool Locally

This project uses the [mypy](https://mypy.readthedocs.io/en/stable/) 
tool which is a static type checker for Python.

> Type checkers help ensure that you’re using variables and functions in your code correctly.
> With mypy, add type hints (PEP 484) to your Python programs, 
> and mypy will warn you when you use those types incorrectly.

The mypy configuration is in the `pyproject.toml` file.

### Run my[py]

Run my[py] on all files in the project.
```shell
  mypy .
```

To run my[py] check on a specific file, follow the pattern `mypy <path_to_file>/<name_of_file>.py --check-untyped-defs`.

Example:
```shell
   mypy version_tag_check/version_tag_check_action.py
``` 

### Expected Output

This is an example of the expected console output after running the tool:
```console
Success: no issues found in 1 source file
```

---

## Run Unit Tests with Pytest

Unit tests are written using the Pytest framework and are located under `tests/unit/`.

To run only unit tests (excluding integration tests), use the following command:
```shell
pytest -v tests/unit/
```

You can modify the directory to control the level of detail or granularity as per your needs.

---

## Run Integration Tests with Pytest

Integration tests are located under `tests/integration/` and are marked with `@pytest.mark.integration`.

These tests run the action entrypoint (`main.py`) in a subprocess and patch `GitHubRepository` in the child process to avoid real network calls.
Inputs are provided via the same environment variables used by the action (`INPUT_GITHUB_TOKEN`, `INPUT_GITHUB_REPOSITORY`, `INPUT_VERSION_TAG`, `INPUT_SHOULD_EXIST`).

Prerequisites:

- Perform the [setup of python venv](#set-up-python-environment).

Run only integration tests:

```shell
pytest -v -m integration tests/integration/
```

Run everything except integration tests:

```shell
pytest -v -m "not integration" tests/
```

---
## Code Coverage with pytest-cov

This project uses the [pytest-cov](https://pypi.org/project/pytest-cov/) plugin to generate test coverage reports.
The objective of the project is to achieve a minimum score of 80 %. We do exclude the `tests/` file from the coverage report.

To generate the coverage report, run the following command:
```shell
pytest --ignore=tests --cov=. tests/ --cov-fail-under=80 --cov-report=html
```

See the coverage report on the path:

```shell
open htmlcov/index.html
```

---
## Releasing

This project uses GitHub Actions for deployment draft creation. The deployment process is semi-automated by a workflow defined in `.github/workflows/release_draft.yml`.

- **Trigger the workflow**: The `release_draft.yml` workflow is triggered on workflow_dispatch.
- **Create a new draft release**: The workflow creates a new draft release in the repository.
- **Finalize the release draft**: Edit the draft release to add a title, description, and any other necessary details related to the GitHub Action.
- **Publish the release**: Once the draft is ready, publish the release to make it publicly available.

---
## Development Flow with GitHub Copilot

This repository is configured to use GitHub Copilot in three main ways:

- GitHub Codespaces / GitHub web UI – PR‑centric, great for reviews and quick changes.
- Local IDE (VS Code) – day‑to‑day coding, navigation and refactoring.
- Web Copilot at https://github.com/copilot – repo‑aware chat in the browser.

All flows rely on:

- `.github/copilot-instructions.md` – repo‑specific context and coding rules.
- `.github/copilot-review-rules.md` – expectations for default and double‑check reviews.
- Optional agent profiles.

### Common Preparation

Before you start, make sure you:

1. Have read `.github/copilot-instructions.md` and `.github/copilot-review-rules.md`.
2. Use `SPEC.md` and `TASKS.md` for any non‑trivial feature.
3. Know which agent to use for the activity (planning, coding, testing, review).

---

### Flow A – GitHub / Codespaces Chat

Use this flow when you:

- Work directly in a GitHub Codespace.
- Do planning, code review or small fixes from the browser.

**Typical steps**

1. **Open context**

   - Open the relevant PR, issue, or file in GitHub / Codespaces.
   - Start a Copilot chat in the Codespace.

2. **Plan with agents (optional)**

   - For epics or larger changes:
     ```markdown
     @copilot (Architect agent) Based on this issue and SPEC.md, outline a 3–5 step plan.
     ```

3. **Implement small changes**

   ```markdown
   @copilot Using .github/copilot-instructions.md, update this file to satisfy TASKS.md item 2.

---
### Flow B – Local IDE (VS Code) Chat

Use this flow for everyday development on your machine.

**Typical steps**

1. Start from SPEC/TASKS
    ```
    @copilot Here is SPEC.md and TASKS.md. Help me implement tasks one by one, starting from task 1. After each task, propose tests before moving on.
    ```

2. Choose the right agent
    - Planning → Architect / BA / PM agent.
    - Coding help → Junior Dev or Senior Dev agent.
    - Test design → Tester / Test Automation agent.

3. Implement + test in small loops
    - Implement one task.
    - Run tests locally and fix issues.
    - Commit when green.

4. Prepare PR and push
    - Keep PRs small and focused.
    - Link SPEC/TASKS and issues in the PR description.

5. Use Copilot review in GitHub
    - Then follow Flow A’s review steps.

---
### Flow C – Web Copilot (github.com/copilot)

Use this flow when you:
- Are away from your IDE or Codespace.
- Want to explore ideas, refactor plans, or multi‑repo questions.
- Need help understanding existing code or architecture before changing it.

**Typical steps**

1. Open Web Copilot
    - Go to https://github.com/copilot and start a new chat.
    - If needed, point Copilot at this repository (by link or name).
2. Explore or clarify before coding
    - Examples:
      ```markdown
      I’m working on <feature> in <repo>. Here is SPEC.md and TASKS.md.
      Summarise the current design and suggest any risky areas to watch.
      ```
      ```markdown
      Show me how version-tag-check validates tags today and where tests live.
      Propose a safe way to extend it for pre-release tags.
      ```
3. Design and planning with agents
    - Use role agents (Architect, BA, PM, Tester) from the web UI if available in your plan.
    - Keep the conversation focused on:
      - Clarifying requirements and edge cases.
      - Proposing plans and test strategies.
      - Generating drafts for SPEC/TASKS or docs.
4. Hand off to IDE or Codespace
    - Once you have a plan or code snippets:
      - Copy relevant parts into local files or a branch in a Codespace.
      - Continue implementation using Flow A or Flow B.

Web Copilot is best for thinking and exploration; final implementation, tests, and reviews should still happen in the IDE/Codespace flows.
