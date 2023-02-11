from random import randint

import requests
from flask import url_for, Blueprint
from leaktopus.requests_cache import CustomCachedSessionWithPickleSupport
from pytest_httpserver import HTTPServer
from requests_cache import BaseCache
from werkzeug import Request, Response


def testRequestsCacheWithCacheSuccess(app,httpserver):
    config = app.config
    config['REQUESTS_CACHE_ENABLED'] = True
    config['REQUESTS_CACHE_BACKEND'] = BaseCache()
    CustomCachedSessionWithPickleSupport.register(app)

    counter = 0

    def handler(request: Request):
        nonlocal counter
        counter += 1
        return Response("Hello, World!", status=200)

    httpserver.expect_request("/test").respond_with_handler(handler)
    assert requests.get(httpserver.url_for("/test")).status_code == 200
    assert requests.get(httpserver.url_for("/test")).text == "Hello, World!"
    assert counter == 1

def testRequestsCacheWithoutCacheSuccess(app,httpserver):
    counter = 0

    def handler(request: Request):
        nonlocal counter
        counter += 1
        return Response("Hello, World!", status=200)

    httpserver.expect_request("/test").respond_with_handler(handler)
    assert requests.get(httpserver.url_for("/test")).status_code == 200
    assert requests.get(httpserver.url_for("/test")).text == "Hello, World!"
    assert counter == 2
