# encoding: utf-8

from unittest import TestCase

from webob import Request

import web
from web.core import Application, Controller


class NestedController(Controller):
    def index(self):
        web.core.response.content_type = "text/plain"
        return "success"

class RootController(Controller):
    nested = NestedController()
    
    def __before__(self, *parts, **data):
        web.core.response.content_type = "text/plain"
        
        return super(RootController, self).__before__(*parts, **data)
    
    def index(self):
        return "success"
    
    def arg(self, foo):
        return "got %s" % (foo, )
    
    def unicode(self):
        return u"Unicode text."


class BasicDispatch(TestCase):
    app = Application.factory(root=RootController, buffet=False, widgets=False, beaker=False, debug=False)
    
    def test_index(self):
        response = Request.blank('/').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "success"
    
    def test_arguments(self):
        response = Request.blank('/arg/bar').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "got bar"
        
        response = Request.blank('/arg?foo=baz').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "got baz"
    
    def test_unicode(self):
        response = Request.blank('/unicode').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.charset.lower() == "utf-8"
        assert response.unicode_body == u"Unicode text."
    
    def test_nested(self):
        response = Request.blank('/nested/').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "success"
        
        response = Request.blank('/nested').get_response(self.app)
        
        assert response.status == "301 Moved Permanently"
        assert 'moved permanently' in response.body.lower()
        assert response.location == 'http://localhost/nested/'
    