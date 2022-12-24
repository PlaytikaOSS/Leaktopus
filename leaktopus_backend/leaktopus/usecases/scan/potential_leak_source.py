from dataclasses import dataclass


@dataclass
class PotentialLeakSource:
    url: str
    name: str
    html_url: str
    last_modified: str
    content: str
    repo_name: str
    repo_description: str
    context: dict
    source: str
