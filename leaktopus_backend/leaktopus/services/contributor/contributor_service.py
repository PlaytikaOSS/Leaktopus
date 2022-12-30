from leaktopus.services.contributor.provider_interface import ContributorProviderInterface


class ContributorException(Exception):
    pass


class ContributorService:
    def __init__(self, contributor_provider: ContributorProviderInterface):
        self.contributor_provider = contributor_provider

    def get_contributors(self, **kwargs):
        return self.contributor_provider.get_contributors(**kwargs)

    def add_contributor(self, leak_id, name, author_email, committer_email, is_organization_domain, **kwargs):
        return self.contributor_provider.add_contributor(leak_id, name, author_email, committer_email,
                                                         is_organization_domain, **kwargs)
