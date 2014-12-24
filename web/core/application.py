# encoding: utf-8

from inspect import ismethod #, isclass
from itertools import chain
#from weakref import WeakKeyDictionary

try:
	from collections import UserDict
except ImportError:  # pragma: no cover
	from userdict import UserDict

#from marrow.logging import Log, DEBUG
#from marrow.logging.formats import LineFormat
from marrow.util.compat import native
from marrow.util.bunch import Bunch
from marrow.package.cache import PluginCache
from marrow.package.loader import load
from marrow.package.host import ExtensionManager
from webob.exc import HTTPException
#from marrow.wsgi.exceptions import HTTPException

from web.core.tarjan import robust_topological_sort
from web.core.response import registry
from web.ext.base import BaseExtension


class ConfigurationException(Exception):
	pass


class MissingRequirement(ConfigurationException):
	pass


class Application(object):
	"""The WebCore WSGI application."""

	__slots__ = ('_cache', 'Context', 'log', 'extensions', 'signals', 'dialect_cache', 'extension_manager')

	SIGNALS = ('start', 'stop', 'graceful', 'prepare', 'dispatch', 'before', 'after', 'mutate', 'transform')

	def __init__(self, root, **config):
		# TODO: Check root via asserts.

		self._cache = dict()  # TODO: WeakKeyDictionary so we don't keep dynamic __lookup__ objects hanging around!

		config = self.prepare_configuration(config)
		self.Context = self.context_factory(root, config)

		self.log = self.Context.log #.name('web.app')

		self.log.debug("Preparing extensions.")

		self.extension_manager = ExtensionManager('web.extension')
		extensions = self.extensions = self.extension_manager.order(config, 'extensions')
		signals = self.signals = self.bind_signals(config, extensions)
		self.dialect_cache = PluginCache('web.dispatch')
		
		for ext in signals.start:
			ext(self.Context)

	def prepare_configuration(self, config):
		config = Bunch(config) if config else Bunch()
		
		# We really need this to be there later.
		if 'extensions' not in config:
			config.extensions = list()
		
		config.extensions.insert(0, BaseExtension())
		
		return config

	def context_factory(self, root, config):
		class Context(dict):
			def __iter__(self):
				return ((i, self[i]) for i in self.keys() if i[0] != '_')
			
			def __getattr__(self, name):
				try:
					return self[name]
				except KeyError:
					pass
				
				raise AttributeError("Unknown attribute: " + name)
			
			def __setattr__(self, name, value):
				self[name] = value
			
			def __delattr__(self, name):
				try:
					del self[name]
				except KeyError:
					pass
				
				raise AttributeError("Unknown attribute: " + name)
		
		Context.app = self
		Context.root = root
		Context.config = config
		
		sep = '\n' + ' ' * 37
		
		Context.log = __import__('logging').getLogger('web.app')
		#Context.log = Log(None, dict(
		#			formatter=LineFormat("{now.ts}  {level.name:<7}  {name:<10}  {text}{data}", sep, sep)
		#		), level=DEBUG).name('base')
		
		return Context
	
	def bind_signals(self, config, extensions):
		signals = Bunch((signal, []) for signal in self.SIGNALS)

		for ext in extensions:
			for mn in self.SIGNALS:
				m = getattr(ext, mn, None)
				if m:
					signals[mn].append(m)
		
		signals.after.reverse()
		signals.mutate.reverse()
		signals.transform.reverse()
		
		return signals
	
	def __call__(self, environ, start_response=None):
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
			handler = e(context.request.environ)

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
				kwargs = getattr(request, 'kwargs', dict())

				#log.data(handler=handler, args=args, kw=kwargs).debug("Endpoint found.")
				log.debug("Endpoint found.")

				for ext in signals.mutate:
					ext(context, handler, args, kwargs)

				if ismethod(handler) and getattr(handler, '__self__', None):
					#__import__('pudb').set_trace()
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
				if ext(context, exc):
					exc = None

			if exc and not safe:
				raise
		else:
			#log.data(response=context.response).debug("Registry processed, returning response.")
			log.debug("Registry processed, returning response.")
			
			for ext in signals.after:
				ext(context, None)
		
		if start_response:  # webob
			return context.response(environ, start_response)
		
		elif False:  # marrow.wsgi.objects
			status, headers, body = result
			start_response(native(status), [(native(i), native(j)) for i, j in headers])
			return body
		
		return result
