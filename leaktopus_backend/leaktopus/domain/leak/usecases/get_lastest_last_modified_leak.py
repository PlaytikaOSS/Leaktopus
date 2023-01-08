from leaktopus.services.leak.leak import Leak


class GetLatestLastModifiedLeakUseCase:
    def get_latest_last_modified_leak(self, leaks: list[Leak], **kwargs) -> Leak:
        if not leaks:
            return None

        latest_leak = max(leaks, key=lambda leak: leak.last_modified)
        return latest_leak

    def execute(self, leaks: list[Leak]) -> Leak:
        return self.get_latest_last_modified_leak(leaks)
