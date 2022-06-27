import leaktopus.common.db_handler as dbh

TEAMS = "teams"

def get_leaks_to_alert(type):
    leaks = dbh.get_leak()
    alerts = dbh.get_alert(type=type)
    new_leaks = []
    if not alerts:
        return leaks
    for leak in leaks:
        new_leak = True
        for alert in alerts:
            if leak["pid"] == alert["leak_id"]:
                new_leak = False
                break
        if new_leak:
            new_leaks.append(leak)
    return new_leaks


def add_alert(leak_id, type):
    dbh.add_alert(leak_id, type)
