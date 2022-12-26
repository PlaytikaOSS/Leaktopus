from flask import current_app, g

from leaktopus.common.db_handler import get_db
from leaktopus.services.alert.alert_service import AlertService
from leaktopus.services.alert.sqlite_provider import AlertSqliteProvider
from leaktopus.services.ignore_pattern.ignore_pattern_service import (
    IgnorePatternService,
)
from leaktopus.services.ignore_pattern.sqlite_ignore_pattern_provider import (
    SqliteIgnorePatternProvider,
)
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.leak.sqlite_provider import LeakSqliteProvider
from leaktopus.services.leaktopus_config.leaktopus_config_service import (
    LeaktopusConfigService,
)
from leaktopus.services.leaktopus_config.initial_config_leaktopus_config_provider import (
    InitialConfigLeaktopusConfigProvider,
)
from leaktopus.services.notification.memory_provider import NotificationMemoryProvider
from leaktopus.services.notification.ms_teams_provider import (
    NotificationMsTeamsProvider,
)
from leaktopus.services.notification.notification_service import NotificationService
from leaktopus.services.notification.slack_provider import NotificationSlackProvider
from leaktopus.services.potential_leak_source_scan_status.potential_leak_source_scan_status_service import (
    PotentialLeakSourceScanStatusService,
)
from leaktopus.services.potential_leak_source_scan_status.sqlite_potential_leak_source_scan_status_provider import (
    SqlitePotentialLeakSourceScanStatusProvider,
)
from leaktopus.utils.common_imports import logger


def provider_config_require_db(config):
    options = config["options"]
    if "db" in config["options"] and config["options"]["db"] is not False:
        options["db"] = get_db()
    return options


def create_leak_service():
    leak_provider = create_leak_provider_from_config(
        current_app.config["SERVICES"]["leak"]
    )
    leak_service = LeakService(leak_provider)
    return leak_service


def create_leak_provider_from_config(config):
    options = provider_config_require_db(config)
    return {"sqlite": LeakSqliteProvider,}[
        config["provider"]
    ](options)


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


def create_notification_provider_from_config(config, provider_type):
    supported_providers = {
        "ms_teams": NotificationMsTeamsProvider,
        "slack": NotificationSlackProvider,
    }

    if provider_type not in config.keys() or provider_type not in supported_providers:
        raise Exception("Unsupported notification provider {}".format(provider_type))

    return supported_providers[provider_type](**config[provider_type])


def create_notification_service(provider_type) -> NotificationService:
    provider = create_notification_provider_from_config(
        current_app.config["NOTIFICATION_CONFIG"], provider_type
    )
    notification_service = NotificationService(provider)
    return notification_service


def create_provider(supported_providers, providers_config):
    provider = None
    for p in providers_config:
        if p not in supported_providers:
            raise Exception("Unsupported provider {}".format(p))

        provider_class = supported_providers[p][0]
        provider_args = supported_providers[p][1]
        provider_args["provider"] = provider
        provider = provider_class(**provider_args)

    return provider


def create_ignore_pattern_service():
    supported_providers = {
        "sqlite": [SqliteIgnorePatternProvider, {"db": get_db()}],
    }
    provider = create_provider(
        supported_providers,
        current_app.config["SERVICES"]["ignore_pattern"]["providers"],
    )
    return IgnorePatternService(
        provider=provider,
    )


def create_leaktopus_config_service():
    supported_providers = {
        "initial_config": [
            InitialConfigLeaktopusConfigProvider,
            {"config": current_app.config["SERVICES"]["leaktopus_config"]["defaults"]},
        ],
    }
    provider = create_provider(
        supported_providers,
        current_app.config["SERVICES"]["leaktopus_config"]["providers"],
    )
    return LeaktopusConfigService(
        provider=provider,
    )


def create_potential_leak_source_scan_status_service():
    supported_providers = {
        "sqlite": [
            SqlitePotentialLeakSourceScanStatusProvider,
            {"db": get_db()},
        ],
    }
    provider = create_provider(
        supported_providers,
        current_app.config["SERVICES"]["potential_leak_source_scan_status"][
            "providers"
        ],
    )
    return PotentialLeakSourceScanStatusService(
        provider=provider,
    )
