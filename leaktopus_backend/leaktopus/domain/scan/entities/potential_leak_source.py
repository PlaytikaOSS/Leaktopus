from dataclasses import dataclass


@dataclass
class PotentialLeakSource:
    url: str
    name: str
    html_url: str
    last_modified: str
    content: str
    context: dict
    source: str
