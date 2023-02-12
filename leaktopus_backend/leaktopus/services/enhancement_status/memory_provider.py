from leaktopus.services.enhancement_status.enhancement_status import EnhancementStatus
from leaktopus.services.enhancement_status.provider_interface import (
    EnhancementStatusProviderInterface,
)
import datetime

class EnhancementStatusMemoryProvider(EnhancementStatusProviderInterface):
    def __init__(self, enhancement_statuses=[], override_methods={}):
        self.enhancement_statuses = enhancement_statuses
        self.override_methods = override_methods

    def get_enhancement_status(self, **kwargs) -> list[EnhancementStatus]:
        filtered_enhancement_statuses = self.enhancement_statuses

        for prop, value in kwargs.items():
            filtered_enhancement_statuses = [
                c for c in filtered_enhancement_statuses
                if getattr(c, prop) == value
            ]

        return (
            self.override_methods["get_enhancement_status"]()
            if "get_enhancement_status" in self.override_methods
            else filtered_enhancement_statuses
        )

    def add_enhancement_status(self, leak_url, search_query, module_key, last_modified, **kwargs) -> EnhancementStatus:
        id = len(self.enhancement_statuses)+1
        now = datetime.datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        enhancement_status = EnhancementStatus(id, leak_url, search_query, module_key, last_modified, created_at, **kwargs)

        self.enhancement_statuses.append(enhancement_status)
        return (
            self.override_methods["add_enhancement_status"]()
            if "add_enhancement_status" in self.override_methods
            else id
        )

    def update_enhancement_status(self, id, **kwargs) -> EnhancementStatus:
        for es in self.enhancement_statuses:
            if es.id == id:
                for prop, value in kwargs.items():
                    setattr(es, prop, value)

                return (
                    self.override_methods["update_enhancement_status"]()
                    if "update_enhancement_status" in self.override_methods
                    else id
                )
