from dataclasses import dataclass

class EnhancementStatusException(Exception):
    pass

@dataclass
class EnhancementStatus:
    id: int
    leak_url: str
    search_query: str
    module_key: str
    last_modified: str
    created_at: str

    def __init__(self, id: int, leak_url: str, search_query: str, module_key: str, last_modified: str, created_at: str, **kwargs):
        self.id = id
        self.leak_url = leak_url
        self.search_query = search_query
        self.module_key = module_key
        self.last_modified = last_modified
        self.created_at = created_at

    def __json__(self):
        return {
            "id": self.id,
            "leak_url": self.leak_url,
            "search_query": self.search_query,
            "module_key": self.module_key,
            "last_modified": self.last_modified,
            "created_at": self.created_at
        }
