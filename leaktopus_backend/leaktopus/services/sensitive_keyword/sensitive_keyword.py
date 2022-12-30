from dataclasses import dataclass

@dataclass
class SensitiveKeyword:
    pid: int
    leak_id: int
    keyword: str
    url: str
    created_at: str

    def __init__(self, pid: int, leak_id: int, keyword: str, url: str, created_at: str, **kwargs):
        self.pid = pid
        self.leak_id = leak_id
        self.keyword = keyword
        self.url = url
        self.created_at = created_at

    def __json__(self):
        return {
            "pid": self.pid,
            "leak_id": self.leak_id,
            "keyword": self.keyword,
            "url": self.url,
            "created_at": self.created_at
        }
