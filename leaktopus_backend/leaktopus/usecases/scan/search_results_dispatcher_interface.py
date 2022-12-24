from abc import abstractmethod
from typing import Protocol

from leaktopus.tasks.potential_leak_source_request import PotentialLeakSourceRequest


class SearchResultsDispatcherInterface(Protocol):
    @abstractmethod
    def dispatch(
        self,
        initial_search_metadata,
        potential_leak_source_request: PotentialLeakSourceRequest,
    ):
        pass
