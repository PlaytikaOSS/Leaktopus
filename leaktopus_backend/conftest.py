import pytest

from leaktopus.app import create_app
from leaktopus.services.alert.alert_service import AlertService
from leaktopus.services.alert.memory_provider import AlertMemoryProvider
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.leak.memory_provider import LeakMemoryProvider
from leaktopus.services.notification.memory_provider import NotificationMemoryProvider
from leaktopus.services.notification.notification_service import NotificationService

from leaktopus.tasks.clients.memory_client import MemoryClient
from leaktopus.tasks.task_manager import TaskManager



@pytest.fixture(name="app")
def app():
    task_manager = TaskManager(MemoryClient(override_tasks={"run_task": lambda: None}))
    app = create_app(task_manager=task_manager, settings_override={
        "TESTING": True
    })
    yield app


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
def factory_task_manager():
    return lambda override_tasks={}: TaskManager(
        MemoryClient(override_tasks=override_tasks)
    )


@pytest.fixture
def factory_notification_service():
    return lambda override_methods={}: NotificationService(
        NotificationMemoryProvider(
            override_methods=override_methods,
            server_url="http://localhost"
        )
    )
