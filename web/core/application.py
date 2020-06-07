"""Primary WSGI application and framework entry point.

You instantiate the `Application` class in order to configure your web application and produce a
WSGI application invokable object. Requests processed when invoked are isolated, so several
instances may be mixed, freely, and will not conflict with each-other.
"""

from logging import DEBUG, Logger, basicConfig, getLogger
from logging.config import dictConfig
from inspect import isfunction

from webob.exc import HTTPException, HTTPNotFound, HTTPInternalServerError

from marrow.package.host import ExtensionManager
from marrow.package.loader import load

from ..ext import args as arguments
from ..ext.base import BaseExtension
from .context import Context
from .dispatch import WebDispatchers
from .extension import WebExtensions
from .typing import Any, Callable, Dict, WSGIEnvironment, WSGIStartResponse, WSGIResponse, Union, Type
from .util import addLoggingLevel
from .view import WebViews

if __debug__:
	from .util import safe_name


class Application:
	"""The WebCore WSGI application.
	
	This glues together a few components:
	
	* Loading and preparation the Application configuration.
	* Simple or verbose logging configuration.
	* Collection and execution of `web.extension` callbacks.
	* WSGI middleware wrapping.
	* The final WSGI application handling requests.
	  * Issue a series of extension callbacks to `prepare` the request context.
	  * Issue a series of extension callbacks to `collect` endpoint arguments, if executable.
	  * Invoke a callable endpoint to retrieve the result, with additional callbacks to perform actions before
	    or after execution of the endpoint, or treat the endpoint as the result.
	  * Identify and execute the view callback associated with the result type to prepare the response.
	  * Return the now prepared response.
	  * After the response has been sent to the client, execute extension `done` callbacks.
	
	The application object is treated as an extension allowing per-application customization utilizing extension
	callbacks (such as rendering custom views on startup) through sub-classing.
	"""
	
	__slots__ = (
			'RequestContext',  # Per-request context class.
			'__call__',  # WSGI request handler.  Dynamically assigned.
			'__context',  # Application context instance.
			'config',  # Application configuration.
			'feature',  # Feature tag announcement; populated by the `provides` of active extensions.
		)
	
	last: bool = True  # Ensure the application callbacks are "last" in processing, dependent upon all extensions.
	
	__context: Context  # The application-scoped context instance.
	_log: Logger = getLogger(__name__)  # An application-scoped Logger instance.
	
	config: dict  # The preserved configuration.
	feature: set  # The set of available feature flags, as collected from enabled extensions.
	RequestContext: Type[Context]  # The class to instantiate to represent the per-request context.
	
	def __init__(self, root:Any, **config) -> None:
		"""Construct the initial ApplicationContext, populate, and prepare the WSGI stack.
		
		No actions other than configuration should happen during construction.
		
		Current configuration is limited to three arguments:
		
		* `root`
		  The object to use as the starting point of dispatch on each request.
		
		* `logging`
		  Either `None` to indicate WebCore should not manipulate the logging configuration (the default), a string
		  representing the logging level to globally configure (such as `"debug"`), or a dictionary configuration to
		  pass to the Python standard logging `dictConfig()` process.
		
		* `extensions` -- a list of configured extension instances, ignoring `BaseExtension` which is automatically
		  added to the extension set.
		"""
		
		if __debug__: self._log.debug("Preparing WebCore application.")
		self.config = self._configure(config)  # Prepare the configuration.
		
		if isfunction(root):  # We need to armour against this turning into a bound method of the context.
			root = staticmethod(root)
		
		# This constructs a basic `ApplicationContext` containing a few of the passed-in values.
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
		
		if __debug__: self._log.debug("WebCore application prepared.")
	
	def _configure(self, config:dict) -> dict:
		"""Prepare the incoming configuration and ensure certain expected values are present.
		
		For example, this ensures BaseExtension is included in the extension list, and populates the logging config.
		"""
		
		exts = ExtensionManager('web.extension')
		extensions = config.setdefault('extensions', [])
		required = {'request', 'response'}
		fulfilled = set()
		
		extensions.append(self)  # Allow the application object itself to register callbacks.
		
		for tag in exts.named:  # Populate any "always enabled" extensions.
			ext = exts.named[tag]
			if not getattr(ext, 'always', False): continue  # We're looking for always-instantiate extensions.
			if any(isinstance(i, ext) for i in extensions): continue  # This, or a derivative, already instantiated.
			extensions.append(ext(**config.get(tag, {})))
		
		for i, ext in enumerate(extensions):  # Expand any named extension references, which will be instantiated.
			if isinstance(ext, str): ext = extensions[i] = load(ext, 'web.extension')(**config.get(ext, {}))
			required.update(getattr(ext, 'needs', ()))
			fulfilled.update(getattr(ext, 'provides', ()))
		
		while required - fulfilled:
			for missing in required - fulfilled:
				ext = load(missing, 'web.extension')
				ext = ext(**config.get(missing, {}))  # Instantiate.
				
				required.update(getattr(ext, 'needs', ()))
				fulfilled.update(getattr(ext, 'provides', ()))
				extensions.append(ext)
				break  # Force re-calculation of missing dependencies.
		
		try:
			addLoggingLevel('trace', DEBUG - 5)
		except AttributeError:
			pass
		
		# Tests are skipped on these as we have no particular need to test Python's own logging mechanism.
		level = config.get('logging', {}).get('level', None)
		if level:  # pragma: no cover
			basicConfig(level=getattr(logging, level.upper()))
		elif 'logging' in config:  # pragma: no cover
			dictConfig(config['logging'])
		
		return config
	
	# This is impractical to test due to the blocking nature of starting a web server interface.
	# Individual adapters are hand-tested for basic operation prior to release.
	def serve(self, service:Union[str,Callable]='auto', **options) -> None:  # pragma: no cover
		"""Initiate a web server service to serve this application.
		
		You can always use the Application instance as a bare WSGI application, of course.  This method is provided as
		a convenience.
		
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
	
	def _execute_endpoint(self, context:Context, endpoint:Callable, signals) -> Any:
		if not callable(endpoint):
			# Endpoints don't have to be functions.
			# They can instead point to what a function would return for view lookup.
			
			if __debug__:
				self._log.debug("Static endpoint located.", extra={'endpoint': repr(endpoint), **context.log_extra})
			
			# Use the result directly, as if it were the result of calling a function or method.
			return endpoint
		
		# Populate any endpoint arguments and allow for chained mutation and validation.
		args, kwargs = [], {}
		
		try:
			for ext in signals.collect: ext(context, endpoint, args, kwargs)
		
		except HTTPException as e:
			result = e
		
		else:
			# If successful in accumulating arguments, finally call the endpoint.
			
			if __debug__:
				self._log.debug("Callable endpoint located and arguments prepared.", extra=dict(
						request = id(context),
						endpoint = safe_name(endpoint),
						endpoint_args = args,
						endpoint_kw = kwargs
					))
			
			try:
				result = endpoint(*args, **kwargs)
			
			except HTTPException as e:
				result = e
		
		# Execute return value transformation callbacks.
		for ext in signals.transform: result = ext(context, endpoint, result)
		
		return result
	
	def application(self, environ: WSGIEnvironment, start_response: WSGIStartResponse) -> WSGIResponse:
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
		
		if is_endpoint:
			try:
				result = self._execute_endpoint(context, handler, signals)  # Process the endpoint.
			except Exception as e:
				self._log.exception("Caught exception attempting to execute the endpoint.")
				result = HTTPInternalServerError(str(e) if __debug__ else "Please see the logs.")
				
				if 'debugger' in context.extension.feature:
					context.response = result
					for ext in signals.after: ext(context)  # Allow signals to clean up early.
					raise
		
		else:  # If no endpoint could be resolved, that's a 404.
			result = HTTPNotFound("Dispatch failed." if __debug__ else None)
		
		if __debug__:
			self._log.debug("Result prepared, identifying view handler.", extra=dict(
					request = id(context),
					result = safe_name(type(result))
				))
		
		# Identify a view capable of handling this result.
		for view in context.view(result):
			if view(context, result): break
		else:
			# We've run off the bottom of the list of possible views.
			raise TypeError("No view could be found to handle: " + repr(type(result)))
		
		if __debug__:
			self._log.debug("View identified, populating response.", extra=dict(
					request = id(context),
					view = repr(view),
				))
		
		for ext in signals.after: ext(context)
		
		def capture_done(response: WSGIResponse) -> WSGIResponse:
			yield from response
			for ext in signals.done: ext(context)
		
		# This is really long due to the fact we don't want to capture the response too early.
		# We need anything up to this point to be able to simply replace `context.response` if needed.
		return capture_done(context.response.conditional_response_app(environ, start_response))
