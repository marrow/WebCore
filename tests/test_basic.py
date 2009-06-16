# encoding: utf-8

from unittest import TestCase

from webob import Request

import web
from web.core import Application

from common import PlainController


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
    
    def _private(self):
        return "no method for you"


class TestApplication(TestCase):
    def test_profile(self):
        app = Application.factory(root=RootController, debug=True, **{'web.static': False, 'web.profile': True})
        
    def test_dotload(self):
        try:
            app = Application.factory(root='web.core.application:Application')
        
        except ValueError:
            pass
        
        else:
            raise Exception
    
    def test_autostatic(self):
        try:
            app = Application.factory(root=RootController, **{'web.static': True})
        
        except AssertionError:
            # The DirectoryApp raises an AssertionError in response to the target folder (./public/) not existing.
            pass
        
        else:
            raise Exception


class BasicDispatch(TestCase):
    app = Application.factory(root=RootController, **{'web.widgets': True, 'web.beaker': True, 'web.debug': True, 'web.compress': True, 'static.path': '/tmp'})
    
    def test_index(self):
        response = Request.blank('/').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "success"
    
    def test_abnormal(self):
        response = Request.blank('/abnormal').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "it works"
    
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
    
    def test_moved_query_string(self):
        response = Request.blank('/nested?foo=bar').get_response(self.app)
        
        assert response.status == "301 Moved Permanently"
        assert 'moved permanently' in response.body.lower()
        assert response.location == 'http://localhost/nested/?foo=bar'
    
    def test_404(self):
        response = Request.blank('/nex').get_response(self.app)
        
        assert response.status == "404 Not Found"
        assert 'not found' in response.body.lower()
        
        response = Request.blank('/_private').get_response(self.app)
        
        assert response.status == "404 Not Found"
        assert 'not found' in response.body.lower()
