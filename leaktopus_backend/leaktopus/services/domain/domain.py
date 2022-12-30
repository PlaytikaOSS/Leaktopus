from dataclasses import dataclass

@dataclass
class Domain:
    pid: int
    leak_id: int
    url: str
    domain: str
    created_at: str

    def __init__(self, pid: int, leak_id: int, url: str, domain: str, created_at: str, **kwargs):
        self.pid = pid
        self.leak_id = leak_id
        self.url = url
        self.domain = domain
        self.created_at = created_at

    def __json__(self):
        return {
            "pid": self.pid,
            "leak_id": self.leak_id,
            "url": self.url,
            "domain": self.domain,
            "created_at": self.created_at
        }
