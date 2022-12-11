from leaktopus.services.alert.alert_service import AlertService
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.notification.notification_service import NotificationService
from leaktopus.utils.common_imports import logger


class SendAlertsNotificationTask:
    def __init__(
        self,
        leak_service: LeakService,
        alert_service: AlertService,
        notification_service: NotificationService,
        **kwargs
    ):
        self.leak_service = leak_service
        self.alert_service = alert_service
        self.notification_service = notification_service

    def run(self):
        notification_type = self.notification_service.get_provider_name()
        # Get new leaks that require new notifications.
        leaks = self.leak_service.get_leaks()
        leaks_to_alert = self.alert_service.get_leaks_to_alert(leaks, notification_type)

        # Send the notifications.
        leaks_notified = self.notification_service.send_notifications(leaks_to_alert)
        logger.info("Sent {} new alerts via {}", len(leaks_notified), notification_type)

        # Add the new notified leaks to DB as alerts.
        for leak in leaks_notified:
            self.alert_service.add_alert(leak.pid, notification_type)

        return leaks_notified
