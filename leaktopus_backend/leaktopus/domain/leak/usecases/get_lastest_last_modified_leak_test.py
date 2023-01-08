import pytest
from datetime import datetime, timedelta

from leaktopus.domain.leak.usecases.get_lastest_last_modified_leak import GetLatestLastModifiedLeakUseCase
from leaktopus.services.leak.leak import Leak




def test_should_return_latest_last_modified_leak(
):
    now = datetime.now()
    two_days_ago = now - timedelta(days=5)
    five_days_ago = now - timedelta(days=5)

    leaks = [
        Leak(2, 'leak_url_2', 'search_query', 'source', '{}', '{}', True, now, five_days_ago.strftime("%Y-%m-%d %H:%M:%S")),
        Leak(1, 'leak_url_1', 'search_query', 'source', '{}', '{}', True, now, now.strftime("%Y-%m-%d %H:%M:%S")),
        Leak(2, 'leak_url_2', 'search_query', 'source', '{}', '{}', True, now, two_days_ago.strftime("%Y-%m-%d %H:%M:%S"))
    ]

    latest_last_modified_leak = GetLatestLastModifiedLeakUseCase().execute(leaks)
    assert latest_last_modified_leak.last_modified == leaks[1].last_modified
