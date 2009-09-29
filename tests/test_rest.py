# encoding: utf-8

from unittest import TestCase

from webob import Request

import web
from web.core import Application, RESTMethod

from common import PlainController



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


class BasicDispatch(TestCase):
    app = Application.factory(root=RootController, **{'web.widgets': False, 'web.beaker': False, 'debug': False, 'web.compress': False})
    
    def test_detection(self):
        response = Request.blank('/detect').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "GET"
        
        request = Request.blank('/detect')
        request.method = 'HEAD'
        response = request.get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == ""
        
        request = Request.blank('/detect')
        request.method = 'POST'
        response = request.get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "POST"
    
    def test_hello(self):
        request = Request.blank('/test')
        request.method = 'GET'
        response = request.get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "My name is world."
        
        request = Request.blank('/test')
        request.method = 'POST'
        request.body = 'name=Alice'
        response = request.get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "Hello Alice!"
        
        request = Request.blank('/test')
        request.method = 'GET'
        response = request.get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "My name is Alice."
    
    def test_allow(self):
        request = Request.blank('/test')
        request.method = 'GET'
        response = request.get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.headers['Allow'].split(', ') == ['GET', 'POST', 'HEAD']
