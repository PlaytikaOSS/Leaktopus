from leaktopus.services.alert.alert import Alert
from leaktopus.services.alert.provider_interface import (
    AlertProviderInterface,
)
import datetime


class AlertMemoryProvider(AlertProviderInterface):
    def __init__(self, alerts=[], override_methods={}):
        self.alerts = alerts
        self.override_methods = override_methods

    def get_alerts(self, **kwargs) -> list[Alert]:
        filtered_alerts = self.alerts

        if "alert_id" in kwargs:
            filtered_alerts = [
                s for s in filtered_alerts
                if s.alert_id == kwargs.get("alert_id")
            ]

        if "sent_time" in kwargs:
            filtered_alerts = [
                s for s in filtered_alerts
                if s.sent_time == kwargs.get("sent_time")
            ]

        if "leak_id" in kwargs:
            filtered_alerts = [
                s for s in filtered_alerts
                if s.leak_id == kwargs.get("leak_id")
            ]

        if "type" in kwargs:
            filtered_alerts = [
                s for s in filtered_alerts
                if s.type == kwargs.get("type")
            ]

        return (
            self.override_methods["get_alerts"]()
            if "get_alerts" in self.override_methods
            else filtered_alerts
        )

    def add_alert(self, leak_id, type, **kwargs):
        new_id = len(self.alerts)+1
        now = datetime.datetime.now()
        sent_time = now.strftime("%Y-%m-%d %H:%M:%S")
        alert = Alert(new_id, sent_time, leak_id, type, **kwargs)

        self.alerts.append(alert)
        return (
            self.override_methods["add_alert"]()
            if "add_alert" in self.override_methods
            else new_id
        )
