# encoding: utf-8

from unittest import TestCase

from webob import Request

import web
from web.core import Application, Controller
from web.extras.templating import template


class RootController(Controller):
    @template('templates.test')
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


test_config = {'debug': True, 'web.widgets': False, 'web.sessions': False, 'web.compress': False, 'web.static': False}


class TestTemplates(TestCase):
    app = Application.factory(root=RootController, **test_config)
    
    def test_decorator(self):
        """Test decorator template generation."""
        response = Request.blank('/decorator').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.body == '<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>It works!</h1></body></html>'
    
    def test_tuple(self):
        """Test """
        response = Request.blank('/tuple').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.body == '<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>It works!</h1></body></html>'
    
    def test_unicode(self):
        response = Request.blank('/unicode').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.charset == 'UTF-8'
        assert response.unicode_body == u'<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>© 2009</h1></body></html>'
    
    def test_template_globals(self):
        response = Request.blank('/variables').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.body == '<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>It works!</h1></body></html>'
    
    def test_exception(self):
        try:
            response = Request.blank('/bad').get_response(self.app)
            
        except TypeError:
            pass
        
        else:
            raise Exception