from leaktopus.domain.scan.contracts.abstract_potential_leak_source_filter import (
    AbstractPotentialLeakSourceFilter,
)


# TODO: This should be fixed after AbstractPotentialLeakSourceFilter is refactored
class PastebinPotentialLeakSourceFilter(AbstractPotentialLeakSourceFilter):
    def extract_star_count(self, potential_leak_source):
        raise NotImplementedError

    def extract_fork_count(self, potential_leak_source):
        raise NotImplementedError
