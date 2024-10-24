from typing import Optional

from version_tag_check.version import Version


class VersionValidator:
    def __init__(self, new_version: Version, existing_versions: list):
        self.new_version = new_version
        self.existing_versions = existing_versions

    def get_latest_version(self) -> Optional[Version]:
        if not self.existing_versions:
            return None
        return max(self.existing_versions)

    def is_valid_increment(self) -> bool:
        latest_version = self.get_latest_version()
        if not latest_version:
            # Any version is valid if no previous versions exist
            return True

        lv = latest_version
        nv = self.new_version

        if nv.major == lv.major:
            if nv.minor == lv.minor:
                return nv.patch == lv.patch + 1
            elif nv.minor == lv.minor + 1:
                return nv.patch == 0
            else:
                return False
        elif nv.major == lv.major + 1:
            return nv.minor == 0 and nv.patch == 0
        else:
            return False
