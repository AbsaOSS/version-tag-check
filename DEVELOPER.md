# Living Documentation Generator - for Developers

- [Project Setup](#project-setup)
- [Run Scripts Locally](#run-scripts-locally)
- [Run Pylint Check Locally](#run-pylint-check-locally)
- [Run Black Tool Locally](#run-black-tool-locally)
- [Run mypy Tool Locally](#run-mypy-tool-locally)
- [Run Unit Tests with Pytest](#run-unit-tests-with-pytest)
- [Code Coverage with pytest-cov](#check-coverage-with-pytest-cov)
- [Releasing](#releasing)

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

Create *.sh file and place it in the project root.

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
export INPUT_GITHUB_REPOSITORY="AbsaOSS/generate-release-notes"

# Run the main script
python main.py
```

---
## Run Pylint Check Locally

This project uses the [Pylint](https://pypi.org/project/pylint/) tool for static code analysis.
Pylint analyses your code without actually running it.
It checks for errors, enforces coding standards, looks for code smells, etc.
We do exclude the `tests/` file from the Pylint check.

Pylint displays a global evaluation score for the code, rated out of a maximum score of 10.0.
We are aiming to keep our code quality high above the score 9.5.

Follow these steps to run Pylint check locally:

- Perform the [setup of python venv](#set-up-python-environment).

### Run Pylint

Run Pylint on all files that are currently tracked by Git in the project.
```shell
pylint $(git ls-files '*.py')
```

To run Pylint on a specific file, follow the pattern `pylint <path_to_file>/<name_of_file>.py`.

Example:
```shell
pylint ./version_tag_check/version_tag_check_action.py
``` 

### Expected Output

This is an example of the expected console output after running the tool:
```
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

The root project file `pyproject.toml` defines the Black tool configuration.
In this project we are accept a line length of 120 characters.
We also exclude the `tests/` files from black formatting.

Follow these steps to format your code with Black locally:

- Perform the [setup of python venv](#set-up-python-environment).

### Run Black

Run Black on all files that are currently tracked by Git in the project.
```shell
black $(git ls-files '*.py')
```

To run Black on a specific file, follow the pattern `black <path_to_file>/<name_of_file>.py`.

Example:
```shell
black ./version_tag_check/version_tag_check_action.py
``` 

### Expected Output

This is an example of the expected console output after running the tool:
```
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

my[py] configuration is in `pyptoject.toml` file.

Follow these steps to format your code with my[py] locally:

### Run my[py]

Run my[py] on all files in the project.
```shell
  mypy .
```

To run my[py] check on a specific file, follow the pattern `mypy <path_to_file>/<name_of_file>.py --check-untyped-defs`.

Example:
```shell
   mypy living_documentation_regime/living_documentation_generator.py
``` 

### Expected Output

This is an example of the expected console output after running the tool:
```
Success: no issues found in 1 source file
```

---


## Run Unit Tests with Pytest

Unit tests are written using the Pytest framework. To run all the tests, use the following command:
```shell
pytest tests/
```

You can modify the directory to control the level of detail or granularity as per your needs.

---
## Check Coverage with pytest-cov

This project uses the [pytest-cov](https://pypi.org/project/pytest-cov/) plugin to generate test coverage reports.
The objective of the project is to achieve a minimum score of 80 %. We do exclude the `tests/` file from the coverage report.

To generate the coverage report, run the following command:
```shell
pytest --ignore=tests/integration --cov=. tests/ --cov-fail-under=80 --cov-report=html
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
