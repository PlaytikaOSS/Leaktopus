from leaktopus.services.secret.secret import Secret
from leaktopus.services.secret.provider_interface import (
    SecretProviderInterface,
)
import datetime


class SecretMemoryProvider(SecretProviderInterface):
    def __init__(self, secrets=[], override_methods={}):
        self.secrets = secrets
        self.override_methods = override_methods

    def get_secrets(self, **kwargs) -> list[Secret]:
        filtered_secrets = self.secrets

        for prop, value in kwargs.items():
            filtered_secrets = [
                s for s in filtered_secrets
                if getattr(s, prop) == value
            ]

        return (
            self.override_methods["get_secrets"]()
            if "get_secrets" in self.override_methods
            else filtered_secrets
        )

    def add_secret(self, leak_id, url, signature_name, match_string, **kwargs):
        pid = len(self.secrets) + 1
        now = datetime.datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        secret = Secret(pid, leak_id, url, signature_name, match_string, created_at, **kwargs)

        self.secrets.append(secret)
        return (
            self.override_methods["add_secret"]()
            if "add_secret" in self.override_methods
            else pid
        )
