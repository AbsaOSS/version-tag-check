# Version Tag Checker

- [Motivation](#motivation)
- [Requirements](#requirements)
- [Inputs](#inputs)
- [Usage](#usage)
- [Developer Guide](#developer-guide)
- [Contribution Guidelines](#contribution-guidelines)
- [License Information](#license-information)
- [Contact or Support Information](#contact-or-support-information)

A GH action for validating version tag sequences and ensuring compliance with versioning standards in repositories.

## Motivation

This action is designed to help maintainers and contributors ensure that version tags are sequenced correctly and comply with versioning standards. It can be used to prevent common issues such as:
- Duplicate version tags on input
- Missing version tags
- Incorrect version sequences
- Non-standard version formats

**The action provides two possible regimes, controlled by the `should-exist` flag:**
- If `should-exist=false` (default): the action checks that the version tag is a valid increment of the latest existing version.
- If `should-exist=true`: the action checks that the specified tag **already exists** in the repository (and skips increment checks).

## Requirements
- **GitHub Token**: A GitHub token with permission to fetch repository data such as Issues and Pull Requests.
- **Python 3.11+**: Ensure you have Python 3.11 installed on your system.

## Inputs

### `github-repository`
- **Description**: The GitHub repository to check for version tags. Example: `AbsaOSS/version-tag-check`.
- **Required**: Yes

### `version-tag`
- **Description**: The version tag to check for in the repository. Example: `v0.1.0`.
- **Required**: Yes

### `should-exist`
- **Description**: Flag to indicate if the version tag should exist in the repository. Set to `true` to check if the version tag should exist. **Note:** Setting this to `true` **disables** the increment validity check.

- **Default**: `false`
- **Required**: No

### `GITHUB_TOKEN`
- **Description**: Your GitHub token for authentication. Store it as a secret and reference it in the workflow file as secrets.GITHUB_TOKEN.
- **Required**: Yes

### Behavior Summary

The action performs three sequential checks:

- **Tag format check** – ensures the tag follows semantic versioning and starts with `v`, e.g., `v1.2.3`.
- **Presence check** – determines whether the version tag is present in the target GitHub repository.
- **Increment check** – verifies that the provided version tag is a valid increment over the latest existing version.
  - ⚠️ This step is **only performed** when `should-exist=false`.

| Tag present in repository (2nd check) | Expected presence of tag in repository | Increment Validity Check (3rd check) | Action final state                                                         |
|---------------------------------------|----------------------------------------|--------------------------------------|----------------------------------------------------------------------------|
| **Yes**                               | `true`                                 | *Skipped*                            | ✅ **Success**: The version tag exists as expected.                         |
| **No**                                | `true`                                 | *Skipped*                            | ❌ **Failure**: The version tag does not exist in the repository.           |
| **Yes**                               | `false`                                | *Skipped*                            | ❌ **Failure**: The version tag should not exist but does.                  |
| **No**                                | `false`                                | ✅ *Valid*                            | ✅ **Success**: The version tag does not exist and is a valid increment.    |
| **No**                                | `false`                                | ❌ *Invalid*                          | ❌ **Failure**: The version tag does not exist and is an **invalid** increment. |

## Usage

### Adding the Action to Your Workflow

See the default action step definition:

```yaml
- uses: actions/setup-python@v5.1.1
  with:
    python-version: '3.11'

- name: Version Tag Check
  id: version_tag_check
  uses: AbsaOSS/version-tag-check@v0.1.0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  
  with:
    github-repository: "{ org }/{ repo }"   # e.g. ${{ github.repository }}
    version-tag: "v0.1.0"
    should-exist: "false"
```

> To troubleshoot a failing run, re-run the GitHub Actions workflow with "debug logging" enabled or run it locally using the script described in [Developer Guide](DEVELOPER.md).

### Supported Version Tags Formats
- `v1.0.0`

### Support Version Weight Comparison
- `v1.0.0` < `v1.0.1` < `v1.1.0` < `v2.0.0`

### Planned Support of Version Tags Formats With Qualifiers
- `v1.0.0-SNAPSHOT`, `v1.0.0-RC[0..9]`, `v1.0.0-RELEASE`, `v1.0.0-HF[0..9]`
- `v1.0.0-ALPHA`, `v1.0.0-BETA`

### Planned Support of Version Weight Comparison With Qualifiers
- `v1.0.0-SNAPSHOT` < `v1.0.0-RC1` < `v1.0.0-RC2` < `v1.0.0-RELEASE` < `v1.0.0-HF1` < `v1.0.0-HF2`
- `v1.0.0-ALPHA` < `v1.0.0-BETA`

## Developer Guide

See this [Developer Guide](DEVELOPER.md) for more technical, development-related information.


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
