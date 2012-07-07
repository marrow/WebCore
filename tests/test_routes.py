# encoding: utf-8

from web.core.dialects.routing import RoutingController
from web.core import Application
from common import WebTestCase


class BarController(object):
    def error(self, foo):
        return "sub"


class RootController(RoutingController):
    def __init__(self):
        super(RootController, self).__init__()

        self._map.connect(None, '/missing', action="missing")
        self._map.connect(None, '/error/{foo}', action="error")
        self._map.connect(None, '/error/{foo}/bar', controller="bar", action="error")
        self._map.connect(None, '/error/{foo}/missing', controller="bar.baz", action="missing")
        self._map.connect(None, '/error/{foo}/none', controller="bar.baz")

    bar = BarController()

    def error(self, foo):
        return repr(foo)


test_config = {'debug': True, 'web.widgets': False, 'web.sessions': False, 'web.compress': False, 'web.static': False}


class TestRESTfulDispatch(WebTestCase):
    app = Application.factory(root=RootController, **test_config)

    def test_basic(self):
        self.assertResponse('/', '404 Not Found', 'text/plain')
        self.assertResponse('/missing', '404 Not Found', 'text/plain')
        self.assertResponse('/error', '404 Not Found', 'text/plain')
        self.assertResponse('/error/', '404 Not Found', 'text/plain')
        self.assertResponse('/error/foo', '200 OK', 'text/html', body="u'foo'")
        self.assertResponse('/error/bar', '200 OK', 'text/html', body="u'bar'")
        self.assertResponse('/error/baz/bar', '200 OK', 'text/html', body="sub")
        self.assertResponse('/error/baz/missing', '404 Not Found', 'text/plain')
        self.assertResponse('/error/baz/none', '404 Not Found', 'text/plain')
