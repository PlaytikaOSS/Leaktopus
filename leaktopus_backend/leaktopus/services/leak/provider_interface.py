from abc import abstractmethod
from typing import Protocol
from leaktopus.services.leak.leak import Leak


class LeakProviderInterface(Protocol):
    @abstractmethod
    def get_leaks(self, **kwargs) -> list[Leak]:
        pass

    @abstractmethod
    def add_leak(
        self,
        url,
        search_query,
        leak_type,
        context,
        iol,
        acknowledged,
        last_modified,
        **kwargs
    ):
        pass

    @abstractmethod
    def update_leak(self, leak_id, **kwargs):
        pass

    @abstractmethod
    def update_iol(self, leak_id, iol):
        pass

    @abstractmethod
    def delete_leak_by_url(self, url, **kwargs):
        pass
