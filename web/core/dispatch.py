# encoding: utf-8

from __future__ import unicode_literals

from collections import deque
from weakref import ref
from inspect import isclass
from marrow.package.host import PluginManager


log = __import__('logging').getLogger(__name__)


class WebDispatchers(PluginManager):
	__isabstractmethod__ = False  # Jerry, it's a weird bug, Jerry.
	
	def __init__(self, ctx):
		self._ctx = ref(ctx)  # Stored for later use during dispatcher configuration.
		# The above is a weak reference to try to reduce cycles; a WebDispatchers instance is itself stored in the context.
		
		super(WebDispatchers, self).__init__('web.dispatch')
	
	def __call__(self, context, handler, path):
		"""Having been bound to an appropriate context, find a handler for the request path.
		
		This is the part of the WebCore request cycle that speaks the Dispatch protocol and performs event bridging.
		
		This requires a context prepared with a `context.extension.signal.dispatch` list and dispatch plugin registry
		as `context.dispatch`.  This does not use `self` to allow for more creative overriding.
		
		For details, see: https://github.com/marrow/WebCore/wiki/Dispatch-Protocol
		"""
		
		is_endpoint = False  # We'll search until we find an endpoint.
		
		# This technically doesn't help Pypy at all, but saves repeated deep lookup in CPython.(E)
		callbacks = context.extension.signal.dispatch  # These extensions want to be notified.
		dispatch = context.dispatch  # Dispatch plugin registry.
		
		if __debug__:
			log.debug("Preparing dispatch.", extra=dict(
					request = id(context.request),
					path = context.request.path_info,
					handler = repr(handler)
				))
		
		try:
			while not is_endpoint:
				# Pull the dispatcher out of the current handler, defaulting to object dispatch.
				dispatcher = self[getattr(handler, '__dispatch__', 'object')]
				
				# Now we need the remaining path elements as a deque.
				path = deque(path.split('/'))
				
				# We don't want a singular leading / in the path to cause trouble.
				if path and not path[0]:
					path.popleft()
				
				# Iterate dispatch events, issuing appropriate callbacks as we descend.
				for consumed, handler, is_endpoint in dispatcher(context, handler, path):
					# DO NOT add production logging statements (ones not wrapped in `if __debug__`) to this callback!
					for ext in callbacks: ext(context, consumed, handler, is_endpoint)
		
		# Dispatch failed utterly.
		except LookupError:
			pass  # `is_endpoint` can only be `False` here.
		
		return is_endpoint, handler if is_endpoint else None
	
	def __getitem__(self, name):
		if hasattr(name, '__call__'):
			return name
		
		# If the dispatcher isn't already executable, it's probably an entry point reference. Load it from cache.
		dispatcher = super(WebDispatchers, self).__getitem__(name)
		
		# If it's uninstantiated, instantiate it.
		if isclass(dispatcher):
			# TODO: Extract **kw settings from context.
			dispatcher = self.named[name] = dispatcher()  # Instantiate and update the entry point cache.
		
		if __debug__:
			log.debug("Loaded dispatcher.", extra=dict(dispatcher=repr(dispatcher)))
		
		return dispatcher
