import requests

from version_tag_check.version import Version


class GitHubRepository:
    def __init__(self, owner: str, repo: str, token: str):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def get_all_tags(self) -> list:
        tags = []
        page = 1
        per_page = 100
        while True:
            response = requests.get(
                f'https://api.github.com/repos/{self.owner}/{self.repo}/tags',
                headers=self.headers,
                params={'per_page': per_page, 'page': page}
            )
            if response.status_code != 200:
                raise Exception(f'Failed to fetch tags: {response.status_code} {response.text}')
            page_tags = response.json()
            if not page_tags:
                break
            for tag_info in page_tags:
                tag_name = tag_info['name']
                try:
                    version = Version(tag_name)
                    tags.append(version)
                except ValueError:
                    pass  # Ignore tags that are not valid versions
            if len(page_tags) < per_page:
                break
            page += 1
        return tags
