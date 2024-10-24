import re
from functools import total_ordering

@total_ordering
class Version:
    VERSION_REGEX = r'^v(\d+)\.(\d+)\.(\d+)$'

    def __init__(self, version_str: str):
        self.version_str = version_str
        self.major = None
        self.minor = None
        self.patch = None
        self.parse()

    def parse(self):
        match = re.match(self.VERSION_REGEX, self.version_str)
        if not match:
            raise ValueError(f'Invalid version format: {self.version_str}')
        self.major, self.minor, self.patch = map(int, match.groups())

    def is_valid_format(self) -> bool:
        return re.match(self.VERSION_REGEX, self.version_str) is not None

    def __eq__(self, other):
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other):
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __str__(self):
        return self.version_str
