"""Rudimentary echo example app, potentially useful for diagnostics.

Demonstrates a serializable object; requires the serialization extension be enabled.
"""

# ## Imports

try:
	from web.dispatch.resource import Resource
except ImportError:
	# TODO: Warning
	raise

log = __import__('logging').getLogger(__name__)  # A standard logging object.



class IP(Resource):
	def get(self):
		return {'ip': self._ctx.request.client_addr}


class Headers:
	def __init__(self, context, container=None):
		self._ctx = context
	
	def __call__(self):
		return dict(self._ctx.request.headers)


class Time(Resource):
	def get(self, tz='utc', format='all'):
		pass



class Echo:
	__slots__ = ('_ctx', '_called', '_args', '_kw')
	
	_called: bool
	_args: tuple
	_kw: dict
	
	def __init__(self, context):
		self._ctx = context
		self._called = False
		self._args = None
		self._kw = None
	
	ip = IP
	headers = Headers
	time = Time
	
	def __call__(self, *args, **kw):
		self.called = True
		self._args = args
		self._kw = kw
		
		return self
	
	def __html__(self, context=None):
		pass
	
	def __json__(self, context=None):
		pass
