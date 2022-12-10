from dataclasses import dataclass


@dataclass
class Leak:
    pid: int
    url: str
    search_query: str
    leak_type: str
    context: str
    leaks: str
    acknowledged: int
    last_modified: int
    created_at: str

    def __init__(self, pid: int, url: str, search_query: str, leak_type: str, context: str, leaks: str, acknowledged: int, last_modified: int, created_at: str, **kwargs):
        self.pid = pid
        self.url = url
        self.search_query = search_query
        self.leak_type = leak_type
        self.context = context
        self.leaks = leaks
        self.acknowledged = acknowledged
        self.last_modified = last_modified
        self.created_at = created_at

    def __json__(self):
        return {
            "pid": self.pid,
            "url": self.url,
            "search_query": self.search_query,
            "leak_type": self.leak_type,
            "context": self.context,
            "leaks": self.leaks,
            "acknowledged": self.acknowledged,
            "last_modified": self.last_modified,
            "created_at": self.created_at
        }
