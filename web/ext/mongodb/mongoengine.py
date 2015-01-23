# encoding: utf-8

import re
from mongoengine import connect

from marrow.package.loader import load
from web.core.compat import native, items


log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


class MongoEngineExtension:
	__slots__ = ('uri', 'db', 'connection', 'cb')
	
	provides = ['db']
	
	def __init__(self, uri, **config):
		self.uri = uri
		
		log.info("Connecting MongoEngine to '%s'.", _safe_uri_replace.sub(r'\1://\2@', uri))
		
		connection = self.connection = dict(tz_aware=True)
		
		scheme, parts = uri.split('://', 1)
		parts, self.db = parts.split('/', 1)
		auth, host = parts.split('@', 1) if '@' in parts else (None, parts)
		
		if scheme != 'mongo':
			raise Exception('The URL must begin with \'mongo://\'!')
		
		connection['host'], connection['port'] = host.split(':') if ':' in host else (host, '27017')
		connection['port'] = int(connection['port'])
		
		if auth:  # pragma: no cover
			connection['username'], _, connection['password'] = auth.partition(':')
		
		# Accept additional keyword arguments to mongoengine.connect() from the INI.
		for k, v in items(config):
			pfx, _, k = k.rpartition('.')
			if pfx != prefix or k in ('alias', 'engine', 'model', 'ready'): continue
			connection[k] = int(v) if v.isdigit() else v
		
		self.cb = config.get('ready', None)
	
	def start(self, context):
		db, connection = self.db, self.connection
		log.debug("Connecting to %s database with connection information: %r", db, connection)
		
		context.mongoengine = connect(db, **connection)
		
		cb = self.cb
		if cb is not None:
			cb = load(cb) if isinstance(cb, native) else cb
			
			if hasattr(cb, '__call__'):
				cb()
