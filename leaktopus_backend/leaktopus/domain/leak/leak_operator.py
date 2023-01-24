from leaktopus.services.leak.leak import Leak


class LeakOperator:
    @staticmethod
    def get_latest_last_modified_leak(leaks: list[Leak]) -> Leak:
        if not leaks:
            return None

        latest_leak = max(leaks, key=lambda leak: leak.last_modified)
        return latest_leak
