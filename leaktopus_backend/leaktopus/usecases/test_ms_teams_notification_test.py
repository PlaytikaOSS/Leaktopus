from leaktopus.services.notification.notification_service import NotificationService
from leaktopus.usecases.ms_teams_notification_test import MSTeamsNotificationTestUseCase


def test_should_send_ms_teams_notification_test(factory_notification_service: NotificationService):
    notification_service = factory_notification_service()
    MSTeamsNotificationTestUseCase(notification_service).execute()
