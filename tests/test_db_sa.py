# encoding: utf-8

from unittest                                   import TestCase

from webob                                      import Request
from paste.registry                             import StackedObjectProxy

import web
from web.core                                   import Application, Controller, request

from common                                     import PlainController

from sqlalchemy.ext.declarative                 import declarative_base


Base = declarative_base()
metadata = Base.metadata
session = StackedObjectProxy()



class RootController(PlainController):
    def index(self):
        return "success"
    
    def in_session(self):
        return repr(session)
    
    def http_error(self):
        raise web.core.http.HTTPInternalServerError
    
    def http_exception(self):
        raise web.core.http.HTTPNoContent()


class TestSASession(TestCase):
    app = Application.factory(root=RootController, debug=False, **{'db.connections': 'test', 'db.test.engine': 'sqlalchemy', 'db.test.model': RootController.__module__, 'db.test.cache': False, 'db.test.sqlalchemy.url': 'sqlite:///:memory:'})
    
    def test_index(self):
        response = Request.blank('/').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "success"
    
    def test_in_session(self):
        response = Request.blank('/in_session').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body.startswith('<sqlalchemy.orm.scoping.ScopedSession')
    
    def test_http_error(self):
        response = Request.blank('/http_error').get_response(self.app)
        assert response.status == "500 Internal Server Error"
    
    def test_http_exception(self):
        response = Request.blank('/http_exception').get_response(self.app)
        assert response.status == "204 No Content"
        