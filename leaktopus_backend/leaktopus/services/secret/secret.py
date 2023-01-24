from dataclasses import dataclass

@dataclass
class Secret:
    pid: int
    leak_id: int
    url: str
    signature_name: str
    match_string: str
    created_at: str

    def __init__(self, pid: int, leak_id: int, url: str, signature_name: str, match_string: str, created_at: str, **kwargs):
        self.pid = pid
        self.leak_id = leak_id
        self.url = url
        self.signature_name = signature_name
        self.match_string = match_string
        self.created_at = created_at

    def __json__(self):
        return {
            "pid": self.pid,
            "leak_id": self.leak_id,
            "url": self.url,
            "signature_name": self.signature_name,
            "match_string": self.match_string,
            "created_at": self.created_at
        }
