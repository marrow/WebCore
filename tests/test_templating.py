# encoding: utf-8

from unittest import TestCase

from webob import Request

import web
from web.core import Application, Controller


class RootController(Controller):
    @web.core.template('templates.test')
    def decorator(self):
        return dict()
    
    def tuple(self):
        return 'templates.test', dict(), dict()
    
    def variables(self):
        return 'templates.variables', dict()
    
    def unicode(self):
        return 'templates.unicode', dict(), {'genshi.default_encoding': None}
    
    def bad(self):
        return 'foo', 'bar'


class TestTemplates(TestCase):
    app = Application.factory(root=RootController, **{'web.widgets': False, 'web.beaker': False, 'debug': False, 'web.compress': False})
    
    def test_decorator(self):
        response = Request.blank('/decorator').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.body == "<html><body><h1>It works!</h1></body></html>"
    
    def test_tuple(self):
        response = Request.blank('/tuple').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.body == "<html><body><h1>It works!</h1></body></html>"
    
    def test_unicode(self):
        response = Request.blank('/unicode').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.charset == 'UTF-8'
        assert response.unicode_body == u"<html><body><h1>© 2009</h1></body></html>"
    
    def test_template_globals(self):
        response = Request.blank('/variables').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.body == "<html><body><h1>It works!</h1></body></html>"
    
    def test_exception(self):
        try:
            response = Request.blank('/bad').get_response(self.app)
            
        except TypeError:
            pass
        
        else:
            raise Exception