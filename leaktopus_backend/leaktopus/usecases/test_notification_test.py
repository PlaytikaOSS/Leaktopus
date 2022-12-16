from leaktopus.services.notification.notification_service import NotificationService
from leaktopus.services.notification_factory.notification_factory import NotificationFactory
from leaktopus.usecases.notification_test import NotificationTestUseCase


def test_should_send_notification_test(factory_notification_factory: NotificationFactory):
    notification_service = factory_notification_factory().new('memory')
    NotificationTestUseCase(notification_service).execute()
