import os

import pytest

from leaktopus.app import create_app
from leaktopus.domain.extractors.domain_extractor import DomainExtractor
from leaktopus.domain.extractors.email_extractor import EmailExtractor
from leaktopus.services.alert.alert_service import AlertService
from leaktopus.services.alert.memory_provider import AlertMemoryProvider
from leaktopus.services.contributor.contributor_service import ContributorService
from leaktopus.services.contributor.memory_provider import ContributorMemoryProvider
from leaktopus.services.domain.domain_service import DomainService
from leaktopus.services.domain.memory_provider import DomainMemoryProvider
from leaktopus.services.enhancement_module.enhancement_module_service import EnhancementModuleService
from leaktopus.services.enhancement_module.memory_provider import EnhancementModuleMemoryProvider
from leaktopus.services.enhancement_status.enhancement_status_service import EnhancementStatusService
from leaktopus.services.enhancement_status.memory_provider import EnhancementStatusMemoryProvider
from leaktopus.services.ignore_pattern.ignore_pattern_provider_interface import (
    IgnorePatternProviderInterface,
)
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.leak.memory_provider import LeakMemoryProvider
from leaktopus.services.notification.memory_provider import NotificationMemoryProvider
from leaktopus.services.notification.notification_service import NotificationService
from leaktopus.services.potential_leak_source_scan_status.interface import (
    PotentialLeakSourceScanStatusProviderInterface,
)
from leaktopus.services.secret.memory_provider import SecretMemoryProvider
from leaktopus.services.secret.secret_service import SecretService
from leaktopus.services.sensitive_keyword.memory_provider import SensitiveKeywordMemoryProvider
from leaktopus.services.sensitive_keyword.sensitive_keyword_service import SensitiveKeywordService
from leaktopus.tasks.clients.memory_client import MemoryClient
from leaktopus.tasks.task_manager import TaskManager


@pytest.fixture()
def app():
    task_manager = TaskManager(MemoryClient(override_tasks={"run_task": lambda: None}))
    app = create_app(task_manager=task_manager, settings_override={
        "TESTING": True,
        "USE_EXPERIMENTAL_REFACTORING": True
    })
    yield app


@pytest.fixture()
def app_db():
    task_manager = TaskManager(MemoryClient(override_tasks={"run_task": lambda: None}))
    app = create_app(task_manager=task_manager, settings_override={
        "TESTING": True,
        "DATABASE_PATH": ":memory:",
        "USE_EXPERIMENTAL_REFACTORING": True
    })
    yield app


@pytest.fixture()
def app_celery_db():
    DB_PATH = "/tmp/leaktopus.sqlite"
    task_manager = TaskManager(MemoryClient(override_tasks={"run_task": lambda: None}))
    app = create_app(task_manager=task_manager, settings_override={
        "TESTING": True,
        "USE_EXPERIMENTAL_REFACTORING": True,
        "DATABASE_PATH": DB_PATH,
        "CELERY_CONFIG": {
            "task_always_eager": True,
            "task_ignore_result": True,
            "task_eager_propagates": True
        }
    })

    yield app

    os.remove(DB_PATH)


# https://github.com/pytest-dev/pytest-flask/issues/69#issuecomment-455828955
@pytest.fixture()
def client(app_celery_db):
    with app_celery_db.test_client() as client:
        yield client


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def factory_leak_service():
    return lambda leaks=[], override_methods={}: LeakService(
        LeakMemoryProvider(leaks=leaks, override_methods=override_methods)
    )


@pytest.fixture()
def add_leak():
    return lambda leak_service: leak_service.add_leak(
        "https://leakexample.com",
        "leaktopus-integration-test",
        "github",
        {},
        # Has two IOLs.
        [{"file_name": "index.html", "file_url": "https://github.com/PlaytikaOSS/Leaktopus/blob/1234567/index.html",
          "org_emails": []},
         {"file_name": "index.htm", "file_url": "https://github.com/PlaytikaOSS/Leaktopus/blob/1234567/index.htm",
          "org_emails": []}],
        False,
        "2000-01-01 00:00:00"
    )


@pytest.fixture()
def factory_alert_service():
    return lambda alerts=[], override_methods={}: AlertService(
        AlertMemoryProvider(alerts=alerts, override_methods=override_methods)
    )


@pytest.fixture()
def factory_task_manager():
    return lambda override_tasks={}: TaskManager(
        MemoryClient(override_tasks=override_tasks)
    )


@pytest.fixture
def factory_notification_service():
    return lambda override_methods={}: NotificationService(
        NotificationMemoryProvider(
            override_methods=override_methods, server_url="http://localhost"
        )
    )


@pytest.fixture
def potential_leak_source_scan_status_provider_mock(mocker):
    return mocker.patch.object(
        PotentialLeakSourceScanStatusProviderInterface, "get_status"
    )


@pytest.fixture
def domain_extractor():
    return DomainExtractor(
        tlds=[
            "com",
            "net",
        ]
    )


@pytest.fixture
def email_extractor():
    return EmailExtractor(
        organization_domains=[
            "example.com",
            "example.net",
        ]
    )


@pytest.fixture
def ignore_pattern_provider_mock(mocker):
    return mocker.patch.object(IgnorePatternProviderInterface, "get_ignore_patterns")


@pytest.fixture()
def factory_domain_service():
    return lambda domains=[], override_methods={}: DomainService(
        DomainMemoryProvider(domains=domains, override_methods=override_methods)
    )


@pytest.fixture()
def factory_contributor_service():
    return lambda contributors=[], override_methods={}: ContributorService(
        ContributorMemoryProvider(contributors=contributors, override_methods=override_methods)
    )


@pytest.fixture()
def factory_secret_service():
    return lambda secrets=[], override_methods={}: SecretService(
        SecretMemoryProvider(secrets=secrets, override_methods=override_methods)
    )


@pytest.fixture()
def factory_sensitive_keyword_service():
    return lambda sensitive_keywords=[], override_methods={}: SensitiveKeywordService(
        SensitiveKeywordMemoryProvider(sensitive_keywords=sensitive_keywords, override_methods=override_methods)
    )

@pytest.fixture()
def factory_enhancement_status_service():
    return lambda enhancement_statuses=[], override_methods={}: EnhancementStatusService(
        EnhancementStatusMemoryProvider(enhancement_statuses=enhancement_statuses, override_methods=override_methods)
    )

@pytest.fixture
def factory_enhancement_module_service():
    return lambda override_methods={}: [EnhancementModuleService(
        EnhancementModuleMemoryProvider(
            override_methods=override_methods
        )
    )]