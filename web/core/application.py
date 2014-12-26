# encoding: utf-8

from __future__ import unicode_literals

import logging

from inspect import ismethod
from itertools import chain
from weakref import WeakKeyDictionary

from webob.exc import HTTPException

from marrow.util.compat import native
from marrow.util.bunch import Bunch
from marrow.package.cache import PluginCache
from marrow.package.loader import load
from marrow.package.host import ExtensionManager

from web.core.response import registry
from web.ext.base import BaseExtension


class Application(object):
	"""The WebCore WSGI application."""
	
	__slots__ = ('_cache', 'Context', 'log', 'extensions', 'features', 'signals', 'dialect_cache', 'extension_manager')
	
	SIGNALS = ('start', 'stop', 'graceful', 'prepare', 'dispatch', 'before', 'after', 'mutate', 'transform')
	
	def __init__(self, root, **config):
		self._cache = WeakKeyDictionary()
		
		config = self.prepare_configuration(config)
		self.Context = self.context_factory(root, config)
		
		self.log = self.Context.log #.name('web.app')
		
		level = config.get('logging', {}).get('level', None)
		if level:
			logging.basicConfig(level=getattr(logging, level.upper()))
		
		self.log.debug("Preparing extensions.")
		
		self.features = []
		self.extension_manager = ExtensionManager('web.extension')
		extensions = self.extensions = self.extension_manager.order(config, 'extensions')
		signals = self.signals = self.bind_signals(config, extensions)
		self.dialect_cache = PluginCache('web.dispatch')
		
		for ext in signals.start:
			ext(self.Context)
	
	def prepare_configuration(self, config):
		"""Prepare the incoming configuration and ensure certain expected values are present.
		
		For example, this ensures BaseExtension is included in the extension list.
		"""
		
		config = Bunch(config) if config else Bunch()
		
		# We really need this to be there.
		if 'extensions' not in config:
			config.extensions = list()
		
		# Always make sure the BaseExtension is present since request/response objects are handy.
		config.extensions.insert(0, BaseExtension())
		
		return config
	
	def context_factory(self, root, config):
		"""Construct a new base Context class for this application.
		
		The Context is a object cooperatively populated with dynamic attributes that also allows dictionary access.
		
		By preparing a base Context ahead of time (and dynamically) we can save some time during each request.
		
		Extensions can add attributes to this class within a `start` callback.
		"""
		
		class Context(object):
			def __iter__(self):
				return ((i, self[i]) for i in dir(self) if i[0] != '_')
			
			def __getitem__(self, name):
				try:
					return getattr(self, name)
				except AttributeError:
					pass
				
				raise KeyError("Unknown attribute: " + name)
			
			def __setitem__(self, name, value):
				setattr(self, name, value)
			
			def __delitem__(self, name):
				try:
					delattr(self, name)
				except AttributeError:
					pass
				
				raise KeyError("Unknown attribute: " + name)
		
		Context.app = self
		Context.root = root
		Context.config = config
		Context.log = logging.getLogger('web.app')
		
		# TODO: marrow.logging
		# sep = '\n' + ' ' * 37
		#Context.log = Log(None, dict(
		#			formatter=LineFormat("{now.ts}  {level.name:<7}  {name:<10}  {text}{data}", sep, sep)
		#		), level=DEBUG).name('base')
		
		return Context
	
	def bind_signals(self, config, extensions):
		"""Enumerate active extensions and aggregate callbacks."""
		
		signals = dict((signal, []) for signal in self.SIGNALS)
		
		for ext in extensions:
			self.features.extend(getattr(ext, 'provides', [])) 
			
			for mn in self.SIGNALS:
				m = getattr(ext, mn, None)
				if m:
					signals[mn].append(m)
		
		# Certain operations act as a stack, i.e. "before" are executed in dependency order, but "after" are executed
		# in reverse dependency order.  This is also the case with "mutate" (incoming) and "transform" (outgoing).
		signals['after'].reverse()
		signals['transform'].reverse()
		
		return Bunch((signal, tuple(signals[signal])) for signal in self.SIGNALS)
	
	def serve(self, service='auto', **options):
		"""Initiate a web server service to serve this application.
		
		You can always use the Application instance as a bare WSGI application, of course.  This method is provided as
		a convienence.
		
		Pass in the name of the service you wish to use, and any additional configuration options appropriate for that
		service.  Almost all services accept `host` and `port` options, some also allow you to specify an on-disk
		`socket`.  By default all web servers will listen to `127.0.0.1` (loopback only) on port 8080.
		"""
		
		service = load(service, 'web.server')
		service(self, **options)
	
	def __call__(self, environ, start_response=None):
		"""Process a single WSGI request/response cycle."""
		
		context = self.Context()
		context.environ = environ
		signals = self.signals
		log = context.log #.name('web.app')
		
		log.debug("Preparing for dispatch.")
		
		for ext in chain(signals.prepare, signals.before):
			ext(context)
		
		exc = None
		
		try:
			router = self.dialect_cache[getattr(context.root, '__dispatch__', 'object')](context.config)
			#self.log.data(router=router).debug("Starting dispatch.")
			self.log.debug("Starting dispatch.")
			
			for consumed, handler, is_endpoint in router(context, context.root):
				for ext in signals.dispatch:
					ext(context, consumed, handler, is_endpoint)
		
		except HTTPException as e:
			return e(context.request.environ, start_response)
		
		count = 0
		
		cache = self._cache
		
		try:
			# We need to determine if the returned object is callable.
			#  If not, continue.
			# Then if the callable is a bound instance method.
			#  If not call with the context as an argument.
			# Otherwise call.
			
			request = context.request
			
			if callable(handler):
				args = list(request.remainder)
				if args and args[0] == '': del args[0]
				
				kwargs = dict()
				for name, value in request.params.items():
					if name.endswith('[]'):
						name = name[:-2]
					if name in kwargs and not isinstance(kwargs[name], list):
						kwargs[name] = [kwargs[name], value]
					elif name in kwargs:
						kwargs[name].append(value)
					else:
						kwargs[name] = value
				
				#log.data(handler=handler, args=args, kw=kwargs).debug("Endpoint found.")
				log.debug("Endpoint found.")
				
				for ext in signals.mutate:
					ext(context, handler, args, kwargs)
				
				# Handle index method calls.
				#__import__('pudb').set_trace()
				if hasattr(handler, '__call__') and ismethod(handler.__call__):
					result = handler(*args, **kwargs)
				elif ismethod(handler) and getattr(handler, '__self__', None):
					result = handler(*args, **kwargs)
				else:
					result = handler(context, *args, **kwargs)
			else:
				result = handler
			
			#log.data(result=result).debug("Endpoint returned, preparing for registry.")
			log.debug("Endpoint returned, preparing for registry.")
			
			for ext in signals.transform:
				ext(context, result)
			
			try:
				# We optimize for the general case whereby callables always return the same type of result.
				kind, renderer, count = cache[handler]
				
				# If the current return value isn't of the expceted type, invalidate the cache.
				# or, if the previous handler can't process the current result, invalidate the cache.
				if not isinstance(result, kind) or not renderer(context, result):
					raise KeyError('Invalidating.')
				
				# Reset the cache miss counter.
				if count > 1:
					cache[handler] = (kind, renderer, 1)
			except (TypeError, KeyError) as e:
				# Perform the expensive deep-search for a valid handler.
				renderer = registry(context, result)
				
				if not renderer:
					raise Exception("Inappropriate return value or return value does not match response registry:\n\t" +
							__import__('pprint').pformat(result))
				
				# If we're updating the cache excessively the optimization is worse than the problem.
				if count > 5:
					renderer = registry
				
				# Update the cache if this isn't a TypeError.
				if not isinstance(e, TypeError):
					cache[handler] = (type(result), renderer, count + 1)
		
		except Exception as exc:
			safe = isinstance(exc, HTTPException)
			
			if safe:
				context.response = exc
			
			#log.data(exc=exc, response=context.response).debug("Registry processed, returning response.")
			log.debug("Registry processed, returning response.")
			
			for ext in signals.after:
				if ext(context, exc):  # Returning a truthy value eats the exception.
					exc = None
			
			if exc and not safe:
				raise
		else:
			#log.data(response=context.response).debug("Registry processed, returning response.")
			log.debug("Registry processed, returning response.")
			
			for ext in signals.after:
				ext(context, None)
		
		return context.response(environ, start_response)
