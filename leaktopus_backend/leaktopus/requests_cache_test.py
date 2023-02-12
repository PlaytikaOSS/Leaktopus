import requests
import requests_cache
from leaktopus.requests_cache import CustomCachedSessionWithPickleSupport
from requests_cache import BaseCache


def testRequestsCacheEnabledSuccess(app, httpserver):
    config = app.config
    config['REQUESTS_CACHE_ENABLED'] = True
    config['REQUESTS_CACHE_BACKEND'] = BaseCache()
    CustomCachedSessionWithPickleSupport.register(app)
    httpserver.expect_request("/enabled").respond_with_data("Enabled!", status=200)
    assert requests.get(httpserver.url_for("/enabled")).status_code == 200
    assert requests.get(httpserver.url_for("/enabled")).text == "Enabled!"
    assert requests_cache.get_cache().response_count() == 1


def testRequestsCacheDisabledSuccess(app, httpserver):
    config = app.config
    config['REQUESTS_CACHE_ENABLED'] = False

    httpserver.expect_request("/disabled").respond_with_data("Disabled!", status=200)
    assert requests.get(httpserver.url_for("/disabled")).status_code == 200
    assert requests.get(httpserver.url_for("/disabled")).text == "Disabled!"
    assert requests_cache.get_cache() is None
