from dataclasses import dataclass


@dataclass
class Alert:
    alert_id: int
    sent_time: str
    leak_id: int
    type: str

    def __init__(self, alert_id: int, sent_time: str, leak_id: int, type: str, **kwargs):
        self.alert_id = alert_id
        self.sent_time = sent_time
        self.leak_id = leak_id
        self.type = type

    def __json__(self):
        return {
            "alert_id": self.alert_id,
            "sent_time": self.sent_time,
            "leak_id": self.leak_id,
            "type": self.type,
        }
