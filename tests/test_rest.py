# encoding: utf-8

from webob import Request

import web
from web.core import Application, RESTMethod

from common import PlainController, WebTestCase



class Hello(RESTMethod):
    def __init__(self):
        super(Hello, self).__init__()
        self.name = 'world'
    
    def get(self):
        return "My name is %s." % (self.name, )
    
    def post(self, name='world'):
        self.name = name
        return "Hello %s!" % (self.name, )


class RootController(PlainController):
    def detect(self):
        return web.core.request.method
    
    test = Hello()


test_config = {'debug': True, 'web.widgets': False, 'web.sessions': False, 'web.compress': False, 'web.static': False}


class TestRESTfulDispatch(WebTestCase):
    app = Application.factory(root=RootController, **test_config)
    
    def test_detection(self):
        self.assertResponse('/detect', _method='HEAD', body="")
        self.assertResponse('/detect', _method='GET', body="GET")
        self.assertResponse('/detect', _method='POST', body="POST")
        self.assertResponse('/detect', _method='PUT', body="PUT")
        self.assertResponse('/detect', _method='DELETE', body="DELETE")
        self.assertResponse('/detect', _method='TRACE', body="TRACE")
        self.assertResponse('/detect', _method='OPTIONS', body="OPTIONS")
    
    def test_failure(self):
        self.assertResponse('/test', '405 Method Not Allowed', 'text/html', 'DELETE')
    
    def test_functional(self):
        self.assertResponse('/test/', body="My name is world.")
        self.assertPostResponse('/test/', dict(name="Alice"), body="Hello Alice!")
        self.assertResponse('/test/', body="My name is Alice.")
    
    def test_options(self):
        response = self.assertResponse('/test/', _method="OPTIONS")
        self.assertEqual(response.headers['Allow'].split(', '), ['GET', 'POST', 'HEAD', 'OPTIONS'])
    
    def test_head(self):
        get = self.assertResponse('/test/')
        self.assertEqual(get.content_length, 17)
        
        head = self.assertResponse('/test/', _method="HEAD", body="")
        # self.assertEqual(head.content_length, 17) # -- buggy: http://trac.pythonpaste.org/pythonpaste/ticket/371
        
        # TODO: Iteratively compare headers.

        
