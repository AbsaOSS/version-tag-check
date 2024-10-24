import os
import sys

from version_tag_check.github_repository import GitHubRepository
from version_tag_check.version import Version
from version_tag_check.version_validator import VersionValidator


class VersionTagCheckAction:
    def __init__(self):
        self.github_token = os.environ.get('INPUT_GITHUB_TOKEN')
        self.version_tag_str = os.environ.get('INPUT_VERSION_TAG')
        self.branch = os.environ.get('INPUT_BRANCH')
        self.fails_on_error = os.environ.get('INPUT_FAILS_ON_ERROR', 'true').lower() == 'true'
        self.github_repository = os.environ.get('INPUT_GITHUB_REPOSITORY')

        # TODO - extra method & add more validations
        if not self.github_token:
            print('GITHUB_TOKEN is not set.')
            sys.exit(1)
        if not self.github_repository:
            print('GITHUB_REPOSITORY is not set.')
            sys.exit(1)

        self.owner, self.repo = self.github_repository.split('/')

    def run(self):
        try:
            new_version = Version(self.version_tag_str)
        except ValueError as e:
            print(str(e))
            self.handle_failure()
            return

        if not new_version.is_valid_format():
            print('Tag does not match the required format "v[0-9]+.[0-9]+.[0-9]+"')
            self.handle_failure()
            return

        repository = GitHubRepository(self.owner, self.repo, self.github_token)
        existing_versions = repository.get_all_tags()

        validator = VersionValidator(new_version, existing_versions)
        if validator.is_valid_increment():
            self.write_output('true')
            print('New tag is valid.')
            sys.exit(0)
        else:
            latest_version = validator.get_latest_version()
            print(f'New tag {self.version_tag_str} is not one version higher than the latest tag {latest_version}.')
            self.handle_failure()

    def write_output(self, valid_value):
        output_file = os.environ.get('GITHUB_OUTPUT')
        if output_file:
            with open(output_file, 'a') as fh:
                print(f'valid={valid_value}', file=fh)
        else:
            print('GITHUB_OUTPUT is not set.')

    def handle_failure(self):
        self.write_output('false')
        if self.fails_on_error:
            sys.exit(1)
        else:
            sys.exit(0)
