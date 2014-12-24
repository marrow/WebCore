# coding: utf-8

from __future__ import unicode_literals, print_function

import pytest

from webob import Request
from webob.exc import HTTPFound

#from marrow.wsgi.objects.request import LocalRequest
#from marrow.wsgi.exceptions import HTTPFound

try:
	from sqlalchemy import Column, Integer, Unicode
	from sqlalchemy.orm import scoped_session, sessionmaker
	from sqlalchemy.ext.declarative import declarative_base
except ImportError:
	pytest.skip("SQLAlchemy not installed.")

from web.core.application import Application
from web.ext.sqlalchemy import SQLAlchemyExtension


Base = declarative_base()


class DummyException(Exception):
	pass


class DummyModel(Base):
	__tablename__ = 'dummy'
	id = Column(Integer, primary_key=True)
	name = Column(Unicode, nullable=False)


def commit_controller(context):
	context.dbsession.add(DummyModel(name='foo'))


def rollback_controller(context):
	context.dbsession.add(DummyModel(name='baz'))
	raise DummyException


def httpexception_controller(context):
	context.dbsession.add(DummyModel(name='bar'))
	raise HTTPFound(location=b'/')


class TestSQLAlchemyExtension(object):
	def setup(self):
		self.Session = scoped_session(sessionmaker())
		self.config = {
				'extensions': [
						SQLAlchemyExtension(url='sqlite:///', session=self.Session, metadata=Base.metadata)
					]
			}
	
	def teardown(self):
		self.Session.remove()
		self.Session.configure(bind=None)
		Base.metadata.bind = None
	
	def test_automatic_commit(self):
		app = Application(commit_controller, **self.config)
		Base.metadata.create_all()
		request = Request()
		status, headers, body = app(request.environ)
		
		obj = self.Session.query(DummyModel).first()
		
		assert status == b'200 OK'
		assert obj.name == 'foo'
		assert obj.id > 0
	
	def test_rollback_on_exception(self):
		app = Application(rollback_controller, **self.config)
		Base.metadata.create_all()
		request = Request()
		
		with raises(DummyException):
			app(request.environ)
		
		assert self.Session.query(DummyModel).first() is None
	
	def test_commit_on_httpexception(self):
		app = Application(httpexception_controller, **self.config)
		Base.metadata.create_all()
		request = Request()
		status, headers, body = app(request.environ)
		
		assert list(self.Session.new) == []  # make sure that either commit or rollback has happened
		
		obj = self.Session.query(DummyModel).first()
		
		assert status == b'302 Found'
		assert obj.name == 'bar'
		assert obj.id > 0
