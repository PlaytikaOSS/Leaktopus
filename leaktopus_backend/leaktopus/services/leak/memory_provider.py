from leaktopus.services.leak.leak import Leak
from leaktopus.services.leak.provider_interface import (
    LeakProviderInterface,
)
import datetime


class LeakMemoryProvider(LeakProviderInterface):
    def __init__(self, leaks=[], override_methods={}):
        self.leaks = leaks
        self.override_methods = override_methods

    def get_leaks(self, **kwargs) -> list[Leak]:
        filtered_leaks = self.leaks

        for prop, value in kwargs.items():
            filtered_leaks = [
                s for s in filtered_leaks
                if s[prop] == value
            ]

        return (
            self.override_methods["get_leaks"]()
            if "get_leaks" in self.override_methods
            else filtered_leaks
        )

    def save_leaks(self, leaks):
        if "save_leaks" in self.override_methods:
            return self.override_methods["save_leaks"](leaks)

        for leak in leaks:
            self.add_leak(
                leak.url,
                leak.search_query,
                leak.leak_type,
                leak.context,
                leak.leaks,
                leak.acknowledged,
                leak.last_modified,
                **leak
            )

    def add_leak(self, url, search_query, leak_type, context, leaks, acknowledged, last_modified, **kwargs):
        pid = len(self.leaks)+1
        now = datetime.datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        leak = Leak(pid, url, search_query, leak_type, context, leaks, acknowledged, last_modified, created_at, **kwargs)

        self.leaks.append(leak)
        return (
            self.override_methods["add_leak"]()
            if "add_leak" in self.override_methods
            else pid
        )

    def update_leak(self, leak_id, **kwargs):
        for leak in self.leaks:
            if leak.pid == leak_id:
                for prop, value in kwargs.items():
                    leak[prop] = value

    def delete_leak_by_url(self, url, **kwargs):
        for leak in self.leaks:
            if leak.url == url:
                self.leaks.remove(leak)
                break
        return (
            self.override_methods["delete_leak_by_url"]
            if "delete_leak_by_url" in self.override_methods
            else None
        )
