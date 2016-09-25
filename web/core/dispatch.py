# encoding: utf-8

# ## Imports

from __future__ import unicode_literals

from collections import deque
from inspect import isclass
from marrow.package.host import PluginManager


# ## Module Globals

# A standard logger object.
log = __import__('logging').getLogger(__name__)


# ## Dispatch Plugin Manager

class WebDispatchers(PluginManager):
	"""WebCore dispatch protocol adapter.
	
	The process of resolving a request path to an endpoint. The dispatch protocol utilized is documented in full
	in the `protocol` project: https://github.com/marrow/protocols/blob/master/dispatch/README.md
	
	The allowable controller structures offered by individual methods of dispatch is documented in the relevant
	dispatch project. Examples of dispatch include:
	
	* Object Dispatch: https://github.com/marrow/web.dispatch.object
	* Registered Routes: https://github.com/marrow/web.dispatch.route
	* Traversal: https://github.com/marrow/web.dispatch.traversal
	
	Others may exist, and dispatch middleware may be available to perform more complex behaviours. The default
	dispatcher if not otherwise configured is object dispatch.
	"""
	
	__isabstractmethod__ = False  # Work around an issue in modern (3.4+) Python due to our instances being callable.
	
	def __init__(self, ctx):
		"""Dispatch registry constructor.
		
		The dispatch registry is not meant to be instantiated by third-party software. Instead, access the registry as
		an attribute of the current Application or Request context: `context.dispatch`
		"""
		
		super(WebDispatchers, self).__init__('web.dispatch')
	
	def __call__(self, context, handler, path):
		"""Having been bound to an appropriate context, find a handler for the request path.
		
		This is the part of the WebCore request cycle that speaks the Dispatch protocol and performs event bridging.
		
		This requires a context prepared with a `context.extension.signal.dispatch` list and dispatch plugin registry
		as `context.dispatch`.  This does not use `self` to allow for more creative overriding.
		"""
		
		is_endpoint = False  # We'll search until we find an endpoint.
		
		# This technically doesn't help Pypy at all, but saves repeated deep lookup in CPython.(E)
		callbacks = context.extension.signal.dispatch  # These extensions want to be notified.
		self = context.dispatch  # Dispatch plugin registry.
		
		if __debug__:
			log.debug("Preparing dispatch.", extra=dict(
					request = id(context.request),
					path = context.request.path_info,
					handler = repr(handler)
				))
		
		# Now we need the remaining path elements as a deque.
		path = path.strip('/')
		path = deque(path.split('/')) if path else deque()
		
		try:
			while not is_endpoint:
				# Pull the dispatcher out of the current handler, defaulting to object dispatch.
				dispatcher = self[getattr(handler, '__dispatch__', 'object')]
				
				# We don't stop if the same dispatcher is loaded twice since some dispatchers might want to do that.
				starting = handler
				
				# Iterate dispatch events, issuing appropriate callbacks as we descend.
				for consumed, handler, is_endpoint in dispatcher(context, handler, path):
					if is_endpoint and not callable(handler) and hasattr(handler, '__dispatch__'):
						is_endpoint = False
					# DO NOT add production logging statements (ones not wrapped in `if __debug__`) to this callback!
					for ext in callbacks: ext(context, consumed, handler, is_endpoint)
				
				# Repeat of earlier, we do this after extensions in case anything above modifies the environ path.
				path = context.environ['PATH_INFO'].strip('/')
				path = deque(path.split('/')) if path else deque()
				
				if not is_endpoint and starting is handler:  # We didn't go anywhere.
					break
		
		# Dispatch failed utterly.
		except LookupError:
			pass  # `is_endpoint` can only be `False` here.
		
		return is_endpoint, handler if is_endpoint else None
	
	def __getitem__(self, dispatcher):
		"""Retrieve a dispatcher from the registry.
		
		This performs some additional work beyond the standard plugin manager in order to construct configured
		instances of the dispatchers instead of simply returning them bare. This allows for configuration and caching
		of these configured dispatchers to happen in a single place.
		"""
		
		name = None
		
		if callable(dispatcher) and not isclass(dispatcher):
			return dispatcher
		
		# If the dispatcher isn't already executable, it's probably an entry point reference. Load it from cache.
		if not isclass(dispatcher):
			name = dispatcher
			dispatcher = super(WebDispatchers, self).__getitem__(dispatcher)
		
		# If it's uninstantiated, instantiate it.
		if isclass(dispatcher):
			# TODO: Extract **kw settings from context.
			dispatcher = dispatcher()  # Instantiate the dispatcher.
			if name:  # Update the entry point cache if loaded by name.
				self.named[name] = dispatcher
		
		if __debug__:
			log.debug("Loaded dispatcher.", extra=dict(dispatcher=repr(dispatcher)))
		
		return dispatcher

