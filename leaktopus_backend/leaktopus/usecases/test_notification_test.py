from leaktopus.services.notification.notification_service import NotificationService
from leaktopus.usecases.notification_test import NotificationTestUseCase


def test_should_send_notification_test(factory_notification_service: NotificationService):
    notification_service = factory_notification_service()
    NotificationTestUseCase(notification_service).execute()
