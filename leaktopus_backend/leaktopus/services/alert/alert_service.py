from leaktopus.services.leak.leak import Leak
from leaktopus.services.alert.alert import Alert
from leaktopus.services.alert.provider_interface import (
    AlertProviderInterface
)


class AlertException(Exception):
    pass


class AlertService:
    def __init__(self, alert_provider: AlertProviderInterface):
        self.alert_provider = alert_provider

    def get_alerts(self, **kwargs) -> list[Alert]:
        return self.alert_provider.get_alerts(**kwargs)

    def add_alert(self, leak_id, type, **kwargs):
        return self.alert_provider.add_alert(leak_id, type, **kwargs)

    def get_leaks_to_alert(self, leaks, type, **kwargs) -> list[Leak]:
        alerts = self.get_alerts(type=type)
        leaks_to_alert = []
        if not alerts:
            return leaks
        for leak in leaks:
            new_leak = True
            for alert in alerts:
                if leak.leak_id == alert.leak_id:
                    new_leak = False
                    break
            if new_leak:
                leaks_to_alert.append(leak)
        return leaks_to_alert
