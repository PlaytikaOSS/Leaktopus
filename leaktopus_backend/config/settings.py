import os
from distutils.util import strtobool
from urllib.parse import urlsplit

from config import celery

SECRET_KEY = os.getenv("SECRET_KEY", None)

SERVER_NAME = os.getenv(
    "SERVER_NAME", "localhost:{0}".format(os.getenv("DOCKER_WEB_PORT", "8000"))
)
HTTPS_ENABLED = os.getenv("HTTPS_ENABLED", 0)

# Flask-Mail.
# MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
# MAIL_PORT = os.getenv('MAIL_PORT', 587)
# MAIL_USE_TLS = bool(strtobool(os.getenv('MAIL_USE_TLS', 'true')))
# MAIL_USE_SSL = bool(strtobool(os.getenv('MAIL_USE_SSL', 'false')))
# MAIL_USERNAME = os.getenv('MAIL_USERNAME', None)
# MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', None)
# MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'contact@local.host')

DATABASE_PATH = os.environ.get("DB_PATH", "/tmp/leaktopus.sqlite")

SERVER_URL = "https" if int(HTTPS_ENABLED) else "http" + "://" + SERVER_NAME

SERVICES = {
    "alert": {
        "provider": "sqlite",
        "options": {
            "db": True,
        },
    },
    "leak": {
        "provider": "sqlite",
        "options": {
            "db": True,
        },
    },
    "domain": {
        "provider": "sqlite",
        "options": {
            "db": True,
        },
    },
    "sensitive_keyword": {
        "provider": "sqlite",
        "options": {
            "db": True,
        },
    },

    "secret": {
        "provider": "sqlite",
        "options": {
            "db": True,
        },
    },

    "contributor": {
        "provider": "sqlite",
        "options": {
            "db": True,
        },
    },
    "ignore_pattern": {"providers": ["sqlite"]},
    "leaktopus_config": {
        "providers": ["initial_config"],
        "defaults": {
            "tlds": ["com", "net", "io", "info"],
            "max_domain_emails": 150,
            "max_non_org_emails": 5,
            "max_fork_count": 2,
            "max_star_count": 2,
        },
    },
    "potential_leak_source_scan_status": {
        "providers": ["sqlite"],
    },
}

NOTIFICATION_CONFIG = {
    "ms_teams": {
        "integration_token": os.environ.get("TEAMS_WEBHOOK_URL"),
        "server_url": SERVER_URL,
    },
    "slack": {
        "integration_token": os.environ.get("SLACK_BOT_TOKEN"),
        "server_url": SERVER_URL,
        "channel": os.environ.get("SLACK_CHANNEL_ID"),
    },
}

# Redis.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
url_parts = urlsplit(REDIS_URL)
REDIS_HOST = url_parts.hostname
REDIS_PORT = url_parts.port
REDIS_DB = url_parts.path.strip("/")

# Github.
GITHUB_USE_APP = os.getenv("GITHUB_USE_APP", False)
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", None)
GITHUB_APP_PRIVATE_KEY_PATH = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH", "/app/private-key.pem")
GITHUB_INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID", None)

# Celery.
CELERY_CONFIG = {
    "broker_url": REDIS_URL,
    "result_backend": REDIS_URL,
    "include": celery.includes,
    "task_max_retries": celery.max_retires,
    "task_reject_on_worker_lost": True,
    "task_acks_late": True,
    "task_serializer": "pickle",
    "result_serializer": "pickle",
    "accept_content": ["pickle"],
    "result_accept_content": ["pickle"],
    "task_always_eager": os.getenv("CELERY_ALWAYS_EAGER", False),
    "task_store_eager_result": os.getenv("CELERY_ALWAYS_EAGER", False),
    "task_eager_propagates": os.getenv("CELERY_ALWAYS_EAGER", False),
}
USE_EXPERIMENTAL_REFACTORING = os.getenv("USE_EXPERIMENTAL_REFACTORING", False)
REQUESTS_CACHE_ENABLED=os.getenv("REQUESTS_CACHE_ENABLED", True)
REQUESTS_CACHE_LOG_LEVEL=os.getenv("REQUESTS_CACHE_LOG_LEVEL", "WARNING")
