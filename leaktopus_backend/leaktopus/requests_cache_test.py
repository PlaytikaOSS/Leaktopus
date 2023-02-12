import requests
from leaktopus.requests_cache import CustomCachedSessionWithPickleSupport
from requests_cache import BaseCache
from werkzeug import Request, Response


def testRequestsCacheWithCacheSuccess(app, httpserver):
    config = app.config
    config['REQUESTS_CACHE_ENABLED'] = False

    counter = 0

    def handler(request: Request):
        nonlocal counter
        counter += 1
        return Response("Hello, World!", status=200)

    httpserver.expect_request("/test").respond_with_handler(handler)
    assert requests.get(httpserver.url_for("/test")).status_code == 200
    assert requests.get(httpserver.url_for("/test")).text == "Hello, World!"
    assert counter == 2

    config['REQUESTS_CACHE_ENABLED'] = True
    config['REQUESTS_CACHE_BACKEND'] = BaseCache()
    CustomCachedSessionWithPickleSupport.register(app)
    assert requests.get(httpserver.url_for("/test")).status_code == 200
    assert requests.get(httpserver.url_for("/test")).text == "Hello, World!"
    assert counter == 3
