# encoding: utf-8
from __future__ import unicode_literals, division, print_function, absolute_import

from marrow.wsgi.exceptions import HTTPException
from marrow.util.compat import basestring

try:
	from sqlalchemy import MetaData, create_engine
	from sqlalchemy.orm import scoped_session
	from sqlalchemy.orm.session import sessionmaker
	from sqlalchemy.orm.scoping import ScopedSession
except ImportError:
	raise ImportError('Unable to import sqlalchemy; pip install sqlalchemy to fix this.')


class SQLAlchemyExtension(object):
	uses = ['transaction']
	provides = ['sqlalchemy']
	
	def __init__(self, url, contextvar='dbsession', session=None, metadata=None, session_opts={}, **kwargs):
		super(SQLAlchemyExtension, self).__init__()
		
		if not isinstance(contextvar, basestring):
			raise TypeError('The "contextvar" option needs to be a string')
		if session is not None and not isinstance(session, ScopedSession):
			raise TypeError('The "session" option needs to be a reference to a ScopedSession instance')
		if metadata is not None and not isinstance(metadata, MetaData):
			raise TypeError('The "metadata" option needs to be a reference to a MetaData instance')
		if not isinstance(session_opts, dict):
			raise TypeError('The "session_opts" option needs to be a dictionary')
		
		self._contextvar = contextvar
		self._engine = create_engine(url, **kwargs)
		self._session = session
		self._metadata = metadata
		self._session_opts = session_opts
	
	def start(self, context):
		# Test the validity of the URL by attempting to make a connection to the target database.
		self._engine.connect().close()
		
		# Create a new ScopedSession if none was given.
		self._session = scoped_session(sessionmaker(**self._session_opts))
		
		# Bind the engine to the session to enable execution of raw SQL.
		self._session.configure(bind=self._engine)
		
		# Bind the engine to the given metadata to facilitate operations like metadata.create_all()
		if self._metadata is not None:
			self._metadata.bind = self._engine
		
		# Add the session to the context
		if hasattr(context, self._contextvar):
			raise Exception('The context already has a variable named "%s"' % self._contextvar)
		setattr(context, self._contextvar, self._session)
	
	def after(self, context, exc=None):
		try:
			if self._session.is_active:
				if exc is None or isinstance(exc, HTTPException):
					self._session.commit()
				else:
					self._session.rollback()
		finally:
			# Return the context-local connection to the connection pool.
			self._session.close()
