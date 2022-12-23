from abc import abstractmethod
from typing import Protocol


class SearchResultsDispatcherInterface(Protocol):
    @abstractmethod
    def dispatch(self, initial_search_metadata, scan_id, organization_domains):
        pass
