import json
from dataclasses import dataclass


@dataclass
class Leak:
    leak_id: int
    url: str
    search_query: str
    type: str
    context: str
    IOL: str
    acknowledged: int
    last_modified: int
    created_at: str

    def __init__(self, leak_id: int, url: str, search_query: str, type: str, context: str, leaks: str,
                 acknowledged: int, last_modified: int, created_at: str, **kwargs):
        self.leak_id = leak_id
        self.url = url
        self.search_query = search_query
        self.type = type
        self.context = self.get_as_object_or_return_list(context)
        self.IOL = self.get_as_object_or_return_list(leaks)
        self.acknowledged = acknowledged
        self.last_modified = last_modified
        self.created_at = created_at

    def get_as_object_or_return_list(self, data):
        if data:
            return json.loads(data)

        return []

    def to_dict(self):
        return self.__dict__

    def __json__(self):
        return {
            "leak_id": self.leak_id,
            "url": self.url,
            "search_query": self.search_query,
            "type": self.type,
            "context": self.context,
            "IOL": self.IOL,
            "acknowledged": self.acknowledged,
            "last_modified": self.last_modified,
            "created_at": self.created_at
        }
