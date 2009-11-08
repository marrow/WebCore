# encoding: utf-8

from unittest import TestCase

from webob import Request
from paste.registry import StackedObjectProxy

import web
from web.core import Application, Controller, request

from common import PlainController, WebTestCase

from sqlalchemy import Column, Unicode
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()
metadata = Base.metadata
session = StackedObjectProxy()



class Foo(Base):
    __tablename__ = 'foo'
    
    name = Column(Unicode(250), primary_key=True)


def populate(a, b):
    pass


def prepare():
    metadata.create_all()


class RootController(PlainController):
    def index(self):
        return "success"
    
    def in_session(self):
        return repr(session)
    
    def http_error(self):
        raise web.core.http.HTTPInternalServerError()
    
    def http_exception(self):
        raise web.core.http.HTTPNoContent()
    
    def http_ok(self):
        raise web.core.http.HTTPOk()


test_config = {
        'debug': True,
        'web.widgets': False,
        'web.sessions': False,
        'web.compress': False,
        'web.static': False,
        'db.connections': 'test',
        'db.test.engine': 'sqlalchemy',
        'db.test.model': RootController.__module__,
        'db.test.cache': False,
        'db.test.sqlalchemy.url': 'sqlite:///:memory:'
    }


class TestSASession(WebTestCase):
    app = Application.factory(root=RootController, **test_config)
    
    def test_index(self):
        self.assertResponse('/', body='success')
    
    def test_in_session(self):
        response = self.assertResponse('/in_session')
        assert response.body.startswith('<sqlalchemy.orm.scoping.ScopedSession')
    
    def test_http_exceptions(self):
        # TODO: Ensure the correct message in the log.
        self.assertResponse('/http_ok', '200 OK', 'text/html')
        self.assertResponse('/http_error', '500 Internal Server Error', 'text/html')
        self.assertResponse('/http_exception', '204 No Content', 'text/html')
