from flask import abort
import json
from leaktopus.common.db_handler import get_leak


def get_leak_by_url(url):
    known_leaks = get_leak(url=url)

    if not known_leaks:
        # New leak.
        return False

    # Get the latest leak (sorted by created_at).
    return known_leaks[0]


def get_leak_by_id(id):
    leaks = fetch_leaks_from_db({"pid": id})
    if not leaks:
        return []

    return leaks


def leaks_result(leaks):
    return {
        "success": True,
        "count": len(leaks),
        "data": leaks
    }


def fetch_leaks_from_db(filters):
    leaks_results = []

    for leak in get_leak(**filters):
        leaks_results.append({
            "leak_id": leak["pid"],
            "url": leak["url"],
            "last_modified": leak["last_modified"],
            "search_query": leak["search_query"],
            "type": leak["leak_type"],
            "created_at": leak["created_at"],
            "context": json.loads(leak["context"]) if leak["context"] else [],
            "secrets": leak["secrets"],
            "domains": leak["domains"],
            "contributors": leak["contributors"],
            "sensitive_keywords": leak["sensitive_keywords"],
            "IOL": json.loads(leak["leaks"]) if leak["leaks"] else []
        })

    return leaks_result(leaks_results)

