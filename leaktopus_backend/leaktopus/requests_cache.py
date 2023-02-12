from logging import getLogger
from multiprocessing import RLock

import loguru
import requests
from flask import current_app
from leaktopus.utils import common_imports
from requests_cache import CachedSession, RedisCache, init_backend


class CustomCachedSessionWithPickleSupport(CachedSession):
    app = None

    def __init__(self, *args, **kwargs):
        with CustomCachedSessionWithPickleSupport.app.app_context():
            config = CustomCachedSessionWithPickleSupport.app.config
            backend = config['REQUESTS_CACHE_BACKEND']
            self.backend = backend
            kwargs['backend'] = backend
            super().__init__(*args, **kwargs)


    def __getstate__(self):
        common_imports.logger.debug('PICKLING')
        self.cache = None
        self.filter_fn = None
        self._lock = None
        self.backend = None
        return self.__dict__

    def __setstate__(self, state):
        common_imports.logger.debug('UNPICKLING')
        with CustomCachedSessionWithPickleSupport.app.app_context():
            config = CustomCachedSessionWithPickleSupport.app.config
            backend = config['REQUESTS_CACHE_BACKEND']
            cache = init_backend('http_cache', backend)
            state['cache'] = cache
            state['_lock'] = RLock()
            state['filter_fn'] = lambda r: True
            self.__dict__.update(state)

    @staticmethod
    def register(app):
        common_imports.logger.debug('Registering CustomCachedSessionWithPickleSupport: {}', app.config["REQUESTS_CACHE_ENABLED"])
        if app.config["REQUESTS_CACHE_ENABLED"]:
            logger = getLogger('requests_cache')
            logger.setLevel(app.config['REQUESTS_CACHE_LOG_LEVEL'])

            CustomCachedSessionWithPickleSupport.app = app
            requests.Session = requests.sessions.Session = CustomCachedSessionWithPickleSupport
