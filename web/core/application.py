# encoding: utf-8

"""Primary WSGI application and framework entry point."""

# ## Imports

from __future__ import unicode_literals

import logging
import logging.config

from inspect import isroutine, isfunction, ismethod, getcallargs
from webob.exc import HTTPException, HTTPNotFound
from marrow.package.loader import load

from .context import Context
from .dispatch import WebDispatchers
from .extension import WebExtensions
from .view import WebViews
from ..ext.base import BaseExtension

if __debug__:
	from .util import safe_name


# ## Module Globals

# A standard Python logger object.
log = __import__('logging').getLogger(__name__)


# ## WSGI Application

class Application(object):
	"""The WebCore WSGI application.
	
	This glues together a few components:
	
	* Loading and preparation the Application configuration.
	* Simple or verbose logging configuration.
	* Collection and execution of `web.extension` callbacks.
	* WSGI middleware wrapping.
	* The final WSGI application handling requests.
	"""
	
	__slots__ = (
			'config',  # Application configuration.
			'feature',  # Feature tag announcement; populated by the `provides` of active extensions.
			
			'__context',  # Application context instance.
			'RequestContext',  # Per-request context class.
			'__call__',  # WSGI request handler.  Dynamically assigned.
		)
	
	def __init__(self, root, **config):
		"""Construct the initial ApplicationContext, populate, and prepare the WSGI stack.
		
		No actions other than configuration should happen during construction.
		
		Current configuration is limited to three arguments:
		
		* `root` -- the object to use as the starting point of dispatch on each request
		* `logging` -- either `None` to indicate WebCore should not manipulate the logging configuration (the
			default), a string representing the logging level to globally configure (such as `"debug"`), or a
			dictionary configuration to pass to the Python standard `logging.dictConfig()` process.
		* `extensions` -- a list of configured extension instances, ignoring `BaseExtension` which is automatically
			added to the extension set.
		"""
		
		self.config = self._configure(config)  # Prepare the configuration.
		
		if __debug__:
			log.debug("Preparing WebCore application.")
		
		if isfunction(root):  # We need to armour against this turning into a bound method of the context.
			root = staticmethod(root)
		
		# This construts a basic `ApplicationContext` containing a few of the passed-in values.
		context = self.__context = Context(app=self, root=root)._promote('ApplicationContext')
		
		# These can't really be deferred to extensions themselves, for fairly obvious chicken/egg reasons.
		exts = context.extension = WebExtensions(context)  # Load extension registry and prepare callbacks.
		context.dispatch = WebDispatchers(context)  # Load dispatch registry.
		context.view = WebViews(context)  # Load the view registry.
		
		# Execute extension startup callbacks; this is the appropriate time to attach descriptors to the context.
		for ext in exts.signal.start: ext(context)
		
		# At this point the context should have been populated with any descriptor protocol additions. Promote the
		# `ApplicationContext` instance to a `RequestContext` class for use during the request/response cycle.
		self.RequestContext = context._promote('RequestContext', instantiate=False)
		
		# Handle WSGI middleware wrapping by extensions and point our __call__ at the result.
		app = self.application
		for ext in exts.signal.middleware: app = ext(context, app)
		self.__call__ = app
		
		if __debug__:  # Mostly useful for timing calculations.
			log.debug("WebCore application prepared.")
	
	def _configure(self, config):
		"""Prepare the incoming configuration and ensure certain expected values are present.
		
		For example, this ensures BaseExtension is included in the extension list, and populates the logging config.
		"""
		config = config or dict()
		
		# We really need this to be there.
		if 'extensions' not in config: config['extensions'] = list()
		
		# Always make sure the BaseExtension is present since request/response objects are handy.
		config['extensions'].insert(0, BaseExtension())
		
		# Tests are skipped on these as we have no particular need to test Python's own logging mechanism.
		level = config.get('logging', {}).get('level', None)
		if level:  # pragma: no cover
			logging.basicConfig(level=getattr(logging, level.upper()))
		elif 'logging' in config:  # pragma: no cover
			logging.config.dictConfig(config['logging'])
		
		return config
	
	# This is impractical to test due to the blocking nature of starting a web server interface.
	# Individual adapters are hand-tested for basic operation prior to release.
	def serve(self, service='auto', **options):  # pragma: no cover
		"""Initiate a web server service to serve this application.
		
		You can always use the Application instance as a bare WSGI application, of course.  This method is provided as
		a convienence.
		
		Pass in the name of the service you wish to use, and any additional configuration options appropriate for that
		service.  Almost all services accept `host` and `port` options, some also allow you to specify an on-disk
		`socket`.  By default all web servers will listen to `127.0.0.1` (loopback only) on port 8080.
		"""
		
		service = load(service, 'web.server')  # We don't bother with a full registry for these one-time lookups.
		
		try:
			service(self, **options)
		except KeyboardInterrupt:  # We catch this as SIG_TERM or ^C are basically the only ways to stop most servers.
			pass
		
		# Notify extensions that the service has returned and we are exiting.
		for ext in self.__context.extension.signal.stop: ext(self.__context)
	
	def _extract_arguments(self, request):
		"""Extract usable args and kwargs from the given request object.
		
		Candidate for promotion to an extension callback. Two approaches come to mind:
		
		* Simple (fast) last-defined-wins.
		* Slower "list if defined multiple times".
			* Optionally merging GET and POST instead of POST overriding.
			* Optionally PHP-style with [] to denote array elements explicitly.
		
		We currently go for the latter without merging or PHP-ness.
		
		TODO: Investigate WebOb's request.urlvars and request.urlargs:
			https://github.com/Pylons/webob/blob/master/webob/request.py#L566-L646
		"""
		
		args = list(request.remainder)
		if args and args[0] == '': del args[0]  # Trim the result of a leading `/`.
	
		def process_kwargs(src):
			kwargs = dict()
			
			for name_, value in src.items():
				if name_ in kwargs and not isinstance(kwargs[name_], list):
					kwargs[name_] = [kwargs[name_], value]
				elif name_ in kwargs:
					kwargs[name_].append(value)
				else:
					kwargs[name_] = value
			
			return kwargs
		
		kwargs = process_kwargs(request.GET)
		kwargs.update(process_kwargs(request.POST))
		
		return args, kwargs
	
	if __debug__:  # This method only exists in development. Really; thus the use of name mangling.
		def __validate_arguments(self, context, endpoint, bound, args, kwargs):
			try:
				if callable(endpoint) and not isroutine(endpoint):
					# Callable Instance
					getcallargs(endpoint.__call__, *args, **kwargs)
				elif bound:
					# Instance Method
					getcallargs(endpoint, *args, **kwargs)
				else:
					# Unbound Method or Function
					getcallargs(endpoint, context, *args, **kwargs)
			
			except TypeError as e:
				# If the argument specification doesn't match, the handler can't process this request.
				# This is one policy. Another possibility is more computationally expensive and would pass only
				# valid arguments, silently dropping invalid ones. This can be implemented as a mutate handler.
				log.error(str(e), extra=dict(
						request = id(context),
						endpoint = safe_name(endpoint),
						endpoint_args = args,
						endpoint_kw = kwargs,
					))
				
				return HTTPNotFound("Incorrect endpoint arguments: " + str(e))
	
	def _execute_endpoint(self, context, endpoint, signals):
		if not callable(endpoint):
			# Endpoints don't have to be functions.
			# They can instead point to what a function would return for view lookup.
			
			if __debug__:
				log.debug("Static endpoint located.", extra=dict(
						request = id(context),
						endpoint = repr(endpoint),
					))
			
			# Use the result directly, as if it were the result of calling a function or method.
			return endpoint
		
		# Our endpoint API states that endpoints recieve as positional parameters all remaining path elements, and
		# as keyword arguments a combination of GET and POST variables with POST taking precedence.
		args, kwargs = self._extract_arguments(context.request)
		
		# Instance methods were handed the context at class construction time via dispatch.
		# The `not isroutine` bit here catches callable instances, a la "index.html" handling.
		bound = not isroutine(endpoint) or (ismethod(endpoint) and getattr(endpoint, '__self__', None) is not None)
	
		# Allow argument transformation; args and kwargs can be manipulated inline.
		for ext in signals.mutate: ext(context, endpoint, args, kwargs)
		
		if __debug__:
			log.debug("Callable endpoint located.", extra=dict(
					request = id(context),
					endpoint = safe_name(endpoint),
					endpoint_args = args,
					endpoint_kw = kwargs
				))
			
			# Make sure the handler can actually accept these arguments when running in development mode.
			# Passing invalid arguments would 500 Internal Server Error on us due to the TypeError exception bubbling up.
			result = self.__validate_arguments(context, endpoint, bound, args, kwargs)
			
			if result:  # Bail if validation returned any truthy value.
				return result
		
		try:
			# Actually call the endpoint.
			if bound:
				result = endpoint(*args, **kwargs)
			else:
				result = endpoint(context, *args, **kwargs)
		
		except HTTPException as e:
			result = e
		
		# Execute return value transformation callbacks.
		for ext in signals.transform: result = ext(context, endpoint, result)
		
		return result
	
	def application(self, environ, start_response):
		"""Process a single WSGI request/response cycle.
		
		This is the WSGI handler for WebCore.  Depending on the presence of extensions providing WSGI middleware,
		the `__call__` attribute of the Application instance will either become this, or become the outermost
		middleware callable.
		
		Most apps won't utilize middleware, the extension interface is preferred for most operations in WebCore.
		They allow for code injection at various intermediary steps in the processing of a request and response.
		"""
		
		context = environ['wc.context'] = self.RequestContext(environ=environ)
		signals = context.extension.signal
		
		# Announce the start of a request cycle. This executes `prepare` and `before` callbacks in the correct order.
		for ext in signals.pre: ext(context)
		
		# Identify the endpoint for this request.
		is_endpoint, handler = context.dispatch(context, context.root, context.environ['PATH_INFO'])
		
		# If no endpoint could be resolved, that's a 404.
		if not is_endpoint:
			# We can't just set the handler to the exception class or instance, because both are callable.
			def handler(_ctx, *args, **kw):  # Yes, this works.  We're just assigning this code obj. to a label.  :3
				"""An endpoint that returns a 404 Not Found error on dispatch failure."""
				return HTTPNotFound("Dispatch failed." if __debug__ else None)  # Not an exceptional event, so don't raise.
		
		result = self._execute_endpoint(context, handler, signals)  # Process the endpoint.
		
				
		if __debug__:
			log.debug("Result prepared, identifying view handler.", extra=dict(
					request = id(context),
					result = repr(result)
				))
		
		# Identify a view capable of handling this result.
		for view in context.view(result):
			if view(context, result): break
		else:
			# We've run off the bottom of the list of possible views.
			raise TypeError("No view could be found to handle: " + repr(type(result)))
		
		if __debug__:
			log.debug("View identified, populating response.", extra=dict(
					request = id(context),
					view = repr(view),
				))
		
		for ext in signals.after: ext(context)
		
		def capture_done(response):
			for chunk in response:
				yield chunk
			
			for ext in signals.done: ext(context)
		
		# This is really long due to the fact we don't want to capture the response too early.
		# We need anything up to this point to be able to simply replace `context.response` if needed.
		return capture_done(context.response.conditional_response_app(environ, start_response))

