from dataclasses import dataclass

@dataclass
class Contributor:
    pid: int
    leak_id: int
    name: str
    author_email: str
    committer_email: str
    is_organization_domain: bool
    created_at: str

    def __init__(self, pid: int, leak_id: int, name: str, author_email: str, committer_email: str, is_organization_domain: bool, created_at: str, **kwargs):
        self.pid = pid
        self.leak_id = leak_id
        self.name = name
        self.author_email = author_email
        self.committer_email = committer_email
        self.is_organization_domain = is_organization_domain
        self.created_at = created_at

    def __json__(self):
        return {
            "pid": self.pid,
            "leak_id": self.leak_id,
            "name": self.name,
            "author_email": self.author_email,
            "committer_email": self.committer_email,
            "is_organization_domain": self.is_organization_domain,
            "created_at": self.created_at
        }
