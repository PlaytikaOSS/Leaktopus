from leaktopus.services.secret.provider_interface import SecretProviderInterface


class SecretException(Exception):
    pass


class SecretService:
    def __init__(self, secret_provider: SecretProviderInterface):
        self.secret_provider = secret_provider

    def get_secrets(self, **kwargs):
        return self.secret_provider.get_secrets(**kwargs)

    def add_secret(self, leak_id, url, signature_name, match_string, **kwargs):
        return self.secret_provider.add_secret(leak_id, url, signature_name, match_string, **kwargs)
