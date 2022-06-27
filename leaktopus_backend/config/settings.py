import os
from distutils.util import strtobool

SECRET_KEY = os.getenv('SECRET_KEY', None)

SERVER_NAME = os.getenv('SERVER_NAME',
                        'localhost:{0}'.format(os.getenv('DOCKER_WEB_PORT',
                                                         '8000')))
HTTPS_ENABLED = os.getenv('HTTPS_ENABLED', 0)

# Flask-Mail.
# MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
# MAIL_PORT = os.getenv('MAIL_PORT', 587)
# MAIL_USE_TLS = bool(strtobool(os.getenv('MAIL_USE_TLS', 'true')))
# MAIL_USE_SSL = bool(strtobool(os.getenv('MAIL_USE_SSL', 'false')))
# MAIL_USERNAME = os.getenv('MAIL_USERNAME', None)
# MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', None)
# MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'contact@local.host')

# Redis.
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Celery.
CELERY_CONFIG = {
    'broker_url': REDIS_URL,
    'result_backend': REDIS_URL,
    'include': [
        'leaktopus.common.scanner_async',
        'leaktopus.common.github_indexer',
        'leaktopus.common.leak_enhancer',
        'leaktopus.common.teams_alerter',
        'leaktopus.common.cron'
    ],
    'task_serializer': 'pickle',
    'result_serializer': 'pickle',
    'accept_content': ['pickle'],
    'result_accept_content': ['pickle'],
    'task_max_retries': None,
}
