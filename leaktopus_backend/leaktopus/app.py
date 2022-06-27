from flask import Flask, g, redirect, url_for, abort
from flask_cors import CORS
from werkzeug.debug import DebuggedApplication
from celery import Celery
from leaktopus.routes.github.github_api import github_api
from leaktopus.routes.system.system_api import system_api
from leaktopus.routes.alerts.alerts_api import alerts_api
from leaktopus.routes.leaks.leaks_api import leaks_api
from leaktopus.routes.scans.scans_api import scans_api
import os
# from leaktopus.extensions import cache, debug_toolbar
from flasgger import Swagger


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name)
    celery.conf.update(app.config.get('CELERY_CONFIG', {}))
    celery.conf.beat_schedule = {
        'run-all-crons-every-minute': {
            'task': 'leaktopus.common.cron.cron_jobs',
            'schedule': int(os.environ.get('CRON_INTERVAL', '60')),
        }
    }

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.
    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__)
    # cache.init_app(app, config={'CACHE_TYPE': 'simple'})

    app.config.from_object('config.settings')
    if settings_override:
        app.config.update(settings_override)

    # Register all our APIs.
    app.register_blueprint(system_api)
    app.register_blueprint(scans_api)
    app.register_blueprint(leaks_api)
    app.register_blueprint(github_api)
    app.register_blueprint(alerts_api)

    extensions(app)

    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).
    :param app: Flask application instance
    :return: None
    """
    CORS(app)
    swagger = Swagger(app)
    # debug_toolbar.init_app(app)
    # mail.init_app(app)
    # csrf.init_app(app)
    # flask_static_digest.init_app(app)

    return None


celery_app = create_celery_app()
