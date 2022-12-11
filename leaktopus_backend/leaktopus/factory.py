from flask import current_app, g

from leaktopus.common.db_handler import get_db
from leaktopus.services.alert.alert_service import AlertService
from leaktopus.services.alert.sqlite_provider import AlertSqliteProvider
from leaktopus.services.notification.ms_teams_provider import MsTeamsProvider
from leaktopus.services.notification.notification_service import NotificationService


def provider_config_require_db(config):
    options = config["options"]
    if "db" in config["options"] and config["options"]["db"] is not False:
        options["db"] = get_db()
    return options


def create_alert_service():
    alert_provider = create_alert_provider_from_config(
        current_app.config["SERVICES"]["alert"]
    )
    alert_service = AlertService(alert_provider)
    return alert_service


def create_alert_provider_from_config(config):
    options = provider_config_require_db(config)
    return {"sqlite": AlertSqliteProvider,}[
        config["provider"]
    ](options)


def create_notification_service():
    notification_provider = create_notification_provider_from_config(
        current_app.config["SERVICES"]["notification"]
    )
    notification_service = NotificationService(notification_provider)
    return notification_service


def create_notification_provider_from_config(config):
    options = provider_config_require_db(config)
    # @todo Generalize to support more notification providers

    return {"ms_teams": MsTeamsProvider,}[
        config["provider"]
    ](**options)

