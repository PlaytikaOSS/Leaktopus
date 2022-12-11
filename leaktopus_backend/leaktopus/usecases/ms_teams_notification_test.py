from leaktopus.services.notification.notification_service import NotificationService


class MSTeamsNotificationTestUseCase:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def execute(self):
        return self.notification_service.send_test()
