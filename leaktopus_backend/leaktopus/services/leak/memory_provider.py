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
                if getattr(s, prop) == value
            ]

        return (
            self.override_methods["get_leaks"]()
            if "get_leaks" in self.override_methods
            else filtered_leaks
        )

    def add_leak(self, url, search_query, type, context, iol, acknowledged, last_modified, **kwargs):
        leak_id = len(self.leaks)+1
        now = datetime.datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        leak = Leak(leak_id, url, search_query, type, context, iol, acknowledged, last_modified, created_at, **kwargs)

        self.leaks.append(leak)
        return (
            self.override_methods["add_leak"]()
            if "add_leak" in self.override_methods
            else leak_id
        )

    def update_leak(self, leak_id, **kwargs):
        for leak in self.leaks:
            if leak.leak_id == leak_id:
                for prop, value in kwargs.items():
                    if prop == "iol":
                        iols = leak.iol
                        # check if the text already exists in the leaks list
                        if value not in iols:
                            # if not, add it to the list
                            iols.append(value)
                            # update the leaks attribute of the leak object
                            setattr(leak, prop, iols)
                    else:
                        setattr(leak, prop, value)

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
