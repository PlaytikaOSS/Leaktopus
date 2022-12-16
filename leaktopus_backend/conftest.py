import pytest

from leaktopus.app import create_app
from leaktopus.services.alert.alert_service import AlertService
from leaktopus.services.alert.memory_provider import AlertMemoryProvider
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.leak.memory_provider import LeakMemoryProvider
from leaktopus.services.notification.memory_provider import NotificationMemoryProvider
from leaktopus.services.notification.notification_service import NotificationService
from leaktopus.services.notification_factory.memory_provider import NotificationFactoryMemoryProvider
from leaktopus.services.notification_factory.notification_factory import NotificationFactory

from leaktopus.tasks.clients.memory_client import MemoryClient
from leaktopus.tasks.task_manager import TaskManager


def create_test_app(app, tmpdir):
    app.config.update(
        {
            "TESTING": True,
            "DATABASE_PATH": tmpdir.join("test.db"),
            "CELERY_CONFIG": {
                "task_always_eager": True,
            }
            # "SERVICES": {}
        }
    )
    # other setup can go here
    return app


@pytest.fixture()
def app_integration():
    app = create_app(
        settings_override={
            "TESTING": True,
            "DATABASE_PATH": ":memory:",
            "CELERY_CONFIG": {
                "task_always_eager": True,
            }
            # "SERVICES": {}
        }
    )  # task_manager=task_manager)
    yield create_test_app(app)


@pytest.fixture(name="app")
def app(tmpdir):
    task_manager = TaskManager(MemoryClient(override_tasks={"run_task": lambda: None}))
    app = create_app(task_manager=task_manager)
    yield create_test_app(app, tmpdir)


# https://github.com/pytest-dev/pytest-flask/issues/69#issuecomment-455828955
@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def factory_leak_service():
    return lambda leaks=[], override_methods={}: LeakService(
        LeakMemoryProvider(
            leaks=leaks, override_methods=override_methods
        )
    )


@pytest.fixture()
def factory_alert_service():
    return lambda alerts=[], override_methods={}: AlertService(
        AlertMemoryProvider(
            alerts=alerts, override_methods=override_methods
        )
    )


@pytest.fixture()
def factory_notification_factory():
    return lambda override_methods={}: NotificationFactory(
        NotificationFactoryMemoryProvider(
            override_methods=override_methods,
        )
    )


@pytest.fixture()
def factory_task_manager():
    return lambda override_tasks={}: TaskManager(
        MemoryClient(override_tasks=override_tasks)
    )
