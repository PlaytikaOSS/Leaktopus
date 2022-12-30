from leaktopus.services.contributor.contributor import Contributor
from leaktopus.services.contributor.provider_interface import (
    ContributorProviderInterface,
)
import datetime

class ContributorMemoryProvider(ContributorProviderInterface):
    def __init__(self, contributors=[], override_methods={}):
        self.contributors = contributors
        self.override_methods = override_methods

    def get_contributors(self, **kwargs) -> list[Contributor]:
        filtered_contributors = self.contributors

        for prop, value in kwargs.items():
            filtered_contributors = [
                c for c in filtered_contributors
                if getattr(c, prop) == value
            ]

        return (
            self.override_methods["get_contributors"]()
            if "get_contributors" in self.override_methods
            else filtered_contributors
        )

    def add_contributor(self, leak_id, name, author_email, committer_email, is_organization_domain, **kwargs):
        pid = len(self.contributors)+1
        now = datetime.datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        contributor = Contributor(pid, leak_id, name, author_email, committer_email, is_organization_domain, created_at, **kwargs)

        self.contributors.append(contributor)
        return (
            self.override_methods["add_contributor"]()
            if "add_contributor" in self.override_methods
            else pid
        )
