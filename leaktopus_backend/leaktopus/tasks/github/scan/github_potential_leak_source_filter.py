from loguru import logger

from leaktopus.usecases.scan.abstract_potential_leak_source_filter import (
    AbstractPotentialLeakSourceFilter,
)


class GithubPotentialLeakSourceFilter(AbstractPotentialLeakSourceFilter):
    def extract_star_count(self, potential_leak_source):
        if potential_leak_source.context['stargazers_count'] is None:
            return 0
        return int(potential_leak_source.context['stargazers_count'])

    def extract_fork_count(self, potential_leak_source):
        if potential_leak_source.context['forks_count'] is None:
            return 0
        return int(potential_leak_source.context['forks_count'])
