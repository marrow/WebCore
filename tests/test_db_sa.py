# encoding: utf-8

from paste.registry import StackedObjectProxy

import web
from web.core import Application

from common import PlainController, WebTestCase

from sqlalchemy import Column, Unicode
from sqlalchemy.ext.declarative import declarative_base
from webob.exc import HTTPInternalServerError



Base = declarative_base()
metadata = Base.metadata
session = StackedObjectProxy()



class Foo(Base):
    __tablename__ = 'foo'
    
    name = Column(Unicode(250), primary_key=True)


def ready(sm):
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
    
    def clear(self):
        for i in session.query(Foo).all():
            session.delete(i)
        
        return "ok"
    
    def create(self, name, die=False):
        o = Foo(name=unicode(name))
        session.add(o)
        
        if die: raise getattr(web.core.http, die)()
        return "ok"
    
    def delete(self, name, die=False):
        o = session.query(Foo).filter_by(name=unicode(name)).one()
        session.delete(o)
        
        if die: raise getattr(web.core.http, die)()
        return "ok"
    
    def load(self, name, die=False):
        o = session.query(Foo).filter_by(name=unicode(name)).one()
        
        if die: raise getattr(web.core.http, die)()
        return "ok"
    
    def rename(self, name, newname, die=False):
        o = session.query(Foo).filter_by(name=unicode(name)).one()
        o.name = unicode(newname)
        
        if die: raise getattr(web.core.http, die)()
        return "ok"
    
    def list(self):
        return u", ".join([i.name for i in session.query(Foo).order_by('name').all()])

    def create_raise(self, name, http_error=False):
        session.add(Foo(name=name))
        session.flush()
        if not http_error:
            raise Exception
        return HTTPInternalServerError()

test_config = {
        'debug': False,
        'web.widgets': False,
        'web.sessions': False,
        'web.compress': False,
        'web.static': False,
        'db.connections': 'test',
        'db.test.engine': 'sqlalchemy',
        'db.test.model': RootController.__module__,
        'db.test.url': 'sqlite:///:memory:',
        'db.test.ready': ready,
    }

app = Application.factory(root=RootController, **test_config)


class TestSASession(WebTestCase):
    app = app
    
    def test_index(self):
        self.assertResponse('/', body='success')
    
    def test_in_session(self):
        response = self.assertResponse('/in_session')
        assert response.body.startswith('<sqlalchemy.orm.session.Session'), response.body
    
    def test_http_exceptions(self):
        self.assertResponse('/http_ok', '200 OK', 'text/plain')
        self.assertResponse('/http_error', '500 Internal Server Error', 'text/plain')
        self.assertResponse('/http_exception', '204 No Content', 'text/html')


class TestSAOperations(WebTestCase):
    app = app

    def setUp(self):
        self.assertResponse('/clear', '200 OK', 'text/plain', body="ok")
        self.assertResponse('/list', '200 OK', 'text/plain', body="")
    
    def test_successful_operations(self):
        self.assertPostResponse('/create', dict(name="foo"), '200 OK', 'text/plain', body="ok")
        self.assertPostResponse('/load', dict(name="foo"), '200 OK', 'text/plain', body="ok")
        self.assertResponse('/list', '200 OK', 'text/plain', body="foo")
        self.assertPostResponse('/rename', dict(name="foo", newname="bar"), '200 OK', 'text/plain', body="ok")
        self.assertResponse('/list', '200 OK', 'text/plain', body="bar")
        self.assertPostResponse('/delete', dict(name="bar"), '200 OK', 'text/plain', body="ok")
        self.assertResponse('/list', '200 OK', 'text/plain', body="")
        
    def test_bad_create(self):
        self.assertPostResponse('/create', dict(name="foo", die="HTTPInternalServerError"),
                '500 Internal Server Error', 'text/plain')
        
        self.assertResponse('/list', '200 OK', 'text/plain', body="")
    
    def test_bad_rename(self):
        self.assertPostResponse('/create', dict(name="foo"), '200 OK', 'text/plain', body="ok")
        self.assertResponse('/list', '200 OK', 'text/plain', body="foo")
        
        self.assertPostResponse('/rename', dict(name="foo", newname="baz", die="HTTPInternalServerError"),
                '500 Internal Server Error', 'text/plain')

        self.assertResponse('/list', '200 OK', 'text/plain', body="foo")

    def test_bad_delete(self):
        self.assertPostResponse('/create', dict(name="foo"), '200 OK', 'text/plain', body="ok")
        self.assertResponse('/list', '200 OK', 'text/plain', body="foo")
        
        self.assertPostResponse('/delete', dict(name="foo", die="HTTPInternalServerError"),
                '500 Internal Server Error', 'text/plain')

        self.assertResponse('/list', '200 OK', 'text/plain', body="foo")
        self.assertPostResponse('/delete', dict(name="foo"), '200 OK', 'text/plain', body="ok")
        self.assertResponse('/list', '200 OK', 'text/plain', body="")

    def test_rollback_on_exception(self):
        try:
            self.assertPostResponse('/create_raise', dict(name="foo", http_error=False))
        except Exception:
            pass
        self.assertResponse('/list', '200 OK', 'text/plain', body="")

        self.assertPostResponse('/create_raise', dict(name="foo", http_error=True),
                '500 Internal Server Error', 'text/plain')
        self.assertResponse('/list', '200 OK', 'text/plain', body="")
