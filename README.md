# Version Tag Checker

- [Motivation](#motivation)
- [Requirements](#requirements)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Usage](#usage)
- [Running Static Code Analysis](#running-static-code-analysis)
- [Run Black Tool Locally](#run-black-tool-locally)
- [Running Unit Test](#running-unit-test)
- [Code Coverage](#code-coverage)
- [Run Action Locally](#run-action-locally)
- [Contribution Guidelines](#contribution-guidelines)
- [License Information](#license-information)
- [Contact or Support Information](#contact-or-support-information)

A GH action for validating version tag sequences and ensuring compliance with versioning standards in repositories.

## Motivation

This action is designed to help maintainers and contributors ensure that version tags are sequenced correctly and comply with versioning standards. It can be used to prevent common issues such as:
- Missing version tags
- Incorrect version sequences
- Non-standard version formats

## Requirements
- **GitHub Token**: A GitHub token with permission to fetch repository data such as Issues and Pull Requests.
- **Python 3.11+**: Ensure you have Python 3.11 installed on your system.

## Inputs

### `GITHUB_TOKEN`
- **Description**: Your GitHub token for authentication. Store it as a secret and reference it in the workflow file as secrets.GITHUB_TOKEN.
- **Required**: Yes

### `github-repository`
- **Description**: The GitHub repository to check for version tags. Example: `AbsaOSS/version-tag-check`.
- **Required**: Yes

### `version-tag`
- **Description**: The version tag to check for in the repository. Example: `v0.1.0`.
- **Required**: Yes

### `branch`
- **Description**: The branch to check for the version tag. Example: `master`.
- **Required**: Yes

### `fails-on-error`
- **Description**: Whether the action should fail if an error occurs.
- **Required**: No
- **Default**: `true`

## Outputs

### `valid`
- **Description**: Whether the version tag is valid.
- **Value**: `true` or `false`

## Usage

### Adding the Action to Your Workflow

See the default action step definition:

```yaml
- name: Version Tag Check
  id: version_tag_check
  uses: AbsaOSS/version-tag-check@v0.1.0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  
  with:
    github-repository: "{ org }/{ repo }"
    version-tag: "v0.1.0"
    branch: "master"
    fails-on-error: "false"
  ```

### Supported Version Tags Formats
- `1.0.0`
- `v1.0.0`

### Support Version Weight Comparison
- `v1.0.0` < `v1.0.1` < `v1.1.0` < `v2.0.0`

### Planned Support of Version Tags Formats With Qualifiers
- `v1.0.0-SNAPSHOT`, `v1.0.0-RC[0..9]`, `v1.0.0-RELEASE`, `v1.0.0-HF[0..9]`
- `v1.0.0-ALPHA`, `v1.0.0-BETA`

### Planned Support of Version Weight Comparison With Qualifiers
- `v1.0.0-SNAPSHOT` < `v1.0.0-RC1` < `v1.0.0-RC2` < `v1.0.0-RELEASE` < `v1.0.0-HF1` < `v1.0.0-HF2`
- `v1.0.0-ALPHA` < `v1.0.0-BETA`

## Running Static Code Analysis

This project uses Pylint tool for static code analysis. Pylint analyses your code without actually running it. It checks for errors, enforces, coding standards, looks for code smells etc.

Pylint displays a global evaluation score for the code, rated out of a maximum score of 10.0. We are aiming to keep our code quality high above the score 9.5.

### Set Up Python Environment
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# run your commands

deactivate
```

This command will also install a Pylint tool, since it is listed in the project requirements.

### Run Pylint
Run Pylint on all files that are currently tracked by Git in the project.
```
pylint $(git ls-files '*.py')
```

To run Pylint on a specific file, follow the pattern `pylint <path_to_file>/<name_of_file>.py`.

Example:
```
pylint ./version_tag_check/version_tag_check_action.py
``` 

## Run Black Tool Locally
This project uses the [Black](https://github.com/psf/black) tool for code formatting.
Black aims for consistency, generality, readability and reducing git diffs.
The coding style used can be viewed as a strict subset of PEP 8.

The project root file `pyproject.toml` defines the Black tool configuration.
In this project we are accepting the line length of 120 characters.

Follow these steps to format your code with Black locally:

### Set Up Python Environment
From terminal in the root of the project, run the following command:

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This command will also install a Black tool, since it is listed in the project requirements.

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
This is the console expected output example after running the tool:
```
All done! ✨ 🍰 ✨
1 file reformatted.
```

## Running Unit Test

Unit tests are written using pytest. To run the tests, use the following command:

```
pytest tests/
```

This will execute all tests located in the tests directory.

## Code Coverage

Code coverage is collected using pytest-cov coverage tool. To run the tests and collect coverage information, use the following command:

```
pytest --cov=. --cov-report=html tests/
```

This will execute all tests located in the tests directory and generate a code coverage report.

See the coverage report on the path:

```
htmlcov/index.html
```

## Run Action Locally
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
export INPUT_BRANCH="main"
export INPUT_FAILS_ON_ERROR="true"
export INPUT_GITHUB_REPOSITORY="AbsaOSS/generate-release-notes"
export GITHUB_OUTPUT="output.txt"   # File to capture outputs

# Remove existing output file if it exists
if [ -f "$GITHUB_OUTPUT" ]; then
  rm "$GITHUB_OUTPUT"
fi

# Run the main script
python main.py

# Display the outputs
echo "Action Outputs:"
cat "$GITHUB_OUTPUT"
```

## Contribution Guidelines

We welcome contributions to the Version Tag Check Action! Whether you're fixing bugs, improving documentation, or proposing new features, your help is appreciated.

### How to Contribute
- **Submit Pull Requests**: Feel free to fork the repository, make changes, and submit a pull request. Please ensure your code adheres to the existing style and all tests pass.
- **Report Issues**: If you encounter any bugs or issues, please report them via the repository's [Issues page](https://github.com/AbsaOSS/version-tag-check/issues).
- **Suggest Enhancements**: Have ideas on how to make this action better? Open an issue to suggest enhancements.

Before contributing, please review our [contribution guidelines](https://github.com/AbsaOSS/version-tag-check/blob/master/CONTRIBUTING.md) for more detailed information.

## License Information

This project is licensed under the Apache License 2.0. It is a liberal license that allows you great freedom in using, modifying, and distributing this software, while also providing an express grant of patent rights from contributors to users.

For more details, see the [LICENSE](https://github.com/AbsaOSS/version-tag-check/blob/master/LICENSE) file in the repository.

## Contact or Support Information

If you need help with using or contributing to Generate Release Notes Action, or if you have any questions or feedback, don't hesitate to reach out:

- **Issue Tracker**: For technical issues or feature requests, use the [GitHub Issues page](https://github.com/AbsaOSS/version-tag-check/issues).
- **Discussion Forum**: For general questions and discussions, join our [GitHub Discussions forum](https://github.com/AbsaOSS/version-tag-check/discussions).
