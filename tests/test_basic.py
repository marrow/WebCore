# encoding: utf-8

from unittest import TestCase

from webob import Request, Response

import web
from web.core import Application

from common import PlainController, WebTestCase


test_config = {'debug': True, 'web.widgets': False, 'web.compress': False, 'web.static.path': '/tmp'}


class TestApplication(TestCase):
    def test_dotload(self):
        self.assertRaises(TypeError, lambda: Application.factory(root='web.core.application:Application', **test_config))
    
    def test_autostatic(self):
        app = Application.factory(root=RootController, **{'web.static': True})
    
    def test_enforceroot(self):
        self.assertRaises(ValueError, lambda: Application.factory(root=dict()))


def wsgi_app(environ, start_response):
    start_response('200 OK', [('Content-type','text/plain')])
    return ['Hello world!\n']


class TestWSGIApplication(WebTestCase):
    app = Application.factory(root=wsgi_app, **test_config)
    
    def test_hello(self):
        self.assertResponse('/', body="Hello world!\n")


class NestedController(PlainController):
    def index(self):
        return "success"


class RootController(PlainController):
    nested = NestedController()

    def index(self, *args, **kw):
        return "success"

    def arg(self, foo):
        return "got %s" % (foo, )

    def unicode(self):
        return u"Unicode text."

    def abnormal(self):
        return ['it works']

    def yields(self):
        yield 'this works '
        yield 'too'

    def _private(self):
        return "no method for you"
    
    def explicit(self):
        return Response(body="hello")
    
    def format(self):
        return web.core.request.format


class TestBasicDispatch(WebTestCase):
    app = Application.factory(root=RootController, **test_config)
    
    def test_paste_debug(self):
        self.assertResponse('/_test_vars')
    
    def test_index(self):
        self.assertResponse('/', body="success")
    
    def test_abnormal(self):
        """Test returning iterators."""
        self.assertResponse('/abnormal', body="it works")
        self.assertResponse('/yields', body="this works too")
    
    def test_arguments(self):
        self.assertResponse('/arg/bar', body="got bar")
        self.assertResponse('/arg?foo=baz', body="got baz")
        self.assertPostResponse('/arg', dict(foo='diz'), body="got diz")
    
    def test_unicode(self):
        self.assertResponse('/unicode', unicode_body=u"Unicode text.", charset='UTF-8')
    
    def test_nested(self):
        self.assertResponse('/nested/', body="success")
    
    def test_nested_rewrite(self):
        self.assertResponse('/nested', '301 Moved Permanently', 'text/html', location='http://localhost/nested/',
            body='301 Moved Permanently\n\nThe resource has been moved to http://localhost/nested/; you should be redirected automatically.  ')
    
    def test_nested_rewrite_query_string(self):
        self.assertResponse('/nested?foo=bar', '301 Moved Permanently', 'text/html', location='http://localhost/nested/?foo=bar')
    
    def test_404(self):
        self.assertResponse('/nex', '404 Not Found', 'text/html', body='404 Not Found\n\nThe resource could not be found.\n\n   ')
    
    def test_private(self):
        self.assertResponse('/_private', '404 Not Found', 'text/html')
    
    def test_explicit_response(self):
        self.assertResponse('/explicit', '200 OK', 'text/html', body="hello")
    
    def test_formats(self):
        self.assertResponse('/format.json', '200 OK', body='json')
        self.assertResponse('/format.html', '200 OK', body='html')
        self.assertResponse('/format.xml', '200 OK', body='xml')
        self.assertResponse('/format.bob', '200 OK', body='bob')


class CustomDialect(web.core.Dialect):
    def __call__(self, request):
        web.core.response.content_type = "text/plain"
        return "it works"


class RootController(web.core.Controller):
    sub = CustomDialect()


class TestDialects(WebTestCase):
    app = Application.factory(root=RootController, **test_config)
    
    def test_base_class(self):
        self.assertRaises(NotImplementedError, lambda: web.core.Dialect()(None))
    
    def test_dialect_transition(self):
        self.assertResponse('/sub/', body='it works')
    


