Copilot instructions for version-tag-check

Purpose
This repo contains a Python 3.11 GitHub Action that validates semantic version tags like v1.2.3 against tags in a GitHub repository.

Context
- Composite action defined in action.yml
- Entry script is main.py
- Core code in version_tag_check (Version, NewVersionValidator, VersionTagCheckAction)
- Inputs are read from env vars: INPUT_GITHUB_TOKEN, INPUT_VERSION_TAG, INPUT_GITHUB_REPOSITORY, INPUT_SHOULD_EXIST

Coding guidelines
- Keep changes small and focused
- Prefer clear, explicit code over clever tricks
- Do not change existing error messages or log texts without a good reason, because tests check them
- Keep behaviour of action inputs stable unless the contract is intentionally updated

Python and style
- Target Python 3.11 or later
- Follow the current patterns in version_tag_check
- Add type hints for new public functions and classes
- Use logging, not print, and keep logging wired through version_tag_check.utils.logging_config

Testing
- Use pytest with tests located in tests/
- Test behaviour: return values, raised errors, log messages, exit codes
- When touching version parsing or increment rules, extend tests in:
	tests/test_version.py
	tests/test_version_validator.py
	tests/test_version_tag_check_action.py
- Mock GitHubRepository and environment variables; do not call the real GitHub API in unit tests

Tooling
- Format with Black using pyproject.toml
- Run Pylint on tracked Python files, excluding tests/, and aim for score 9.5 or higher
- Run mypy and prefer fixing types instead of ignoring errors
- Use pytest-cov and keep coverage at or above 80 percent

Architecture notes
- Action must work on a GitHub Actions runner with only requirements.txt dependencies
- Keep Version and NewVersionValidator free of I/O and environment access
- Route new behaviour that affects action inputs or outputs through VersionTagCheckAction

Pull Request
- When opening a Pull Request, always include a section formatted as follows:

Release Notes:
- Change number 1
- Change number 2

Guidelines:
- Begin the section with the heading `Release Notes:` (including the colon).
- List each user-facing change as a separate bullet point.
- Use clear, concise language for each change.

File overview
- main.py: sets up logging and runs the action
- action.yml: composite action definition
- version_tag_check/version.py: Version model and comparison
- version_tag_check/version_validator.py: new version increment rules
- version_tag_check/version_tag_check_action.py: orchestration and input validation
- version_tag_check/github_repository.py: GitHub API wrapper
- version_tag_check/utils/: helpers including gh_action and logging_config

Review rules
- See `.github/copilot-review-rules.md` for default and double-check review expectations.

Common commands
- Create and activate venv, install deps:
  - python3 -m venv .venv
  -	source .venv/bin/activate
  - pip install -r requirements.txt
- Run tests:
  - pytest tests/
- Run coverage:
  - pytest --ignore=tests/integration --cov=. tests/ --cov-fail-under=80 --cov-report=html
- Format and lint:
  - black
  - pylint --ignore=tests $(git ls-files "*.py")
  - mypy .

Learned rules
- Keep error messages stable; tests assert on exact strings
- Do not change exit codes for existing failure scenarios
