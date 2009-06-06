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
        assert Request.blank('/').get_response(self.app).status == "200 OK"
        assert Request.blank('/').get_response(self.app).content_type == "text/plain"
        assert Request.blank('/').get_response(self.app).body == "success"
    
    def test_arguments(self):
        assert Request.blank('/arg/bar').get_response(self.app).status == "200 OK"
        assert Request.blank('/arg/bar').get_response(self.app).content_type == "text/plain"
        assert Request.blank('/arg/bar').get_response(self.app).body == "got bar"
        
        assert Request.blank('/arg?foo=baz').get_response(self.app).status == "200 OK"
        assert Request.blank('/arg?foo=baz').get_response(self.app).content_type == "text/plain"
        assert Request.blank('/arg?foo=baz').get_response(self.app).body == "got baz"
    
    def test_unicode(self):
        assert Request.blank('/unicode').get_response(self.app).status == "200 OK"
        assert Request.blank('/unicode').get_response(self.app).content_type == "text/plain"
        assert Request.blank('/unicode').get_response(self.app).charset.lower() == "utf-8"
        assert Request.blank('/unicode').get_response(self.app).unicode_body == u"Unicode text."
    
    def test_nested(self):
        assert Request.blank('/nested/').get_response(self.app).status == "200 OK"
        assert Request.blank('/nested/').get_response(self.app).content_type == "text/plain"
        assert Request.blank('/nested/').get_response(self.app).body == "success"
        
        assert Request.blank('/nested').get_response(self.app).status == "301 Moved Permanently"
        assert 'moved permanently' in Request.blank('/nested').get_response(self.app).body.lower()
        assert Request.blank('/nested').get_response(self.app).location == 'http://localhost/nested/'
    