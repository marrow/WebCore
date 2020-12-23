"""Primary WSGI application and framework entry point.

You instantiate the `Application` class in order to configure your web application and produce a
WSGI application invokable object. Requests processed when invoked are isolated, so several
instances may be mixed, freely, and will not conflict with each-other.
"""

import logging
from logging import DEBUG, Logger, basicConfig, getLogger
from logging.config import dictConfig
from inspect import isfunction
from sys import flags

from webob.exc import HTTPException, HTTPNotFound, HTTPInternalServerError

from marrow.package.host import ExtensionManager
from marrow.package.loader import load

from ..ext import args as arguments
from .context import Context
from .dispatch import WebDispatchers
from .extension import WebExtensions
from .typing import Any, Callable, Dict, WSGIEnvironment, WSGIStartResponse, WSGIResponse, Union, Type
from .util import addLoggingLevel
from .view import WebViews

if __debug__:
	from .util import safe_name
	
	if flags.dev_mode:
		MIME_ICON = {
				'application': "\uf1c9",
				'audio': "\uf1c7",
				'font': "\uf031",
				'image': "\uf1c5",
				'text': "\uf0f6",
				'unknown': "\uf016",
				'video': "\uf1c8",
				'multipart': "\uf68e",
				'message': "\uf865",
				'model': "\ue706",
				
				'application/gzip': "\uf1c6",
				'application/pdf': "\uf1c1",
				'application/vnd.rar': "\uf1c6",
				'application/x-7z-compressed': "\uf1c6",
				'application/x-bzip2': "\uf1c6",
				'application/x-rar': "\uf1c6",
				'application/x-rar-compressed': "\uf1c6",
				'application/x-tar': "\uf1c6",
				'application/x-zip-compressed': "\uf1c6",
				'application/zip': "\uf1c6",
				'multipart/x-zip': "\uf1c6",
				'text/csv': "\uf717",
				'text/html': "\uf1c9",
				'text/tsv': "\uf717",
				'application/vnd.ms-fontobject': "\uf031",
			}


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
			'RequestContext', '__context', 'config', 'feature',  # See below.
			'__call__',  # WSGI request handler.  Dynamically assigned as the result of WSGI middleware wrapping.
		)
	
	last: bool = True  # Ensure the application callbacks are "last" in processing, dependent upon all extensions.
	
	__context: Context  # The application-scoped context instance.
	_log: Logger = getLogger(__name__)  # An application-scoped Logger instance.
	
	config: dict  # The preserved initial application configuration.
	feature: set  # The set of available feature flags, as collected from the `provides` of enabled extensions.
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
		
		if __debug__: self._log.info("Preparing WebCore application.")
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
		
		if __debug__: self._log.info("WebCore application prepared.")
	
	def _configure(self, config:dict) -> dict:
		"""Prepare the incoming configuration and ensure certain expected values are present.
		
		For example, this ensures BaseExtension is included in the extension list, and populates the logging config.
		"""
		
		try:  # Add this very early on, to allow extensions and the managers to utilize this logging level.
			addLoggingLevel('trace', DEBUG - 5)
		except AttributeError:
			pass
		
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
		
		level = config.get('logging', 'debug' if flags.dev_mode else ('info' if __debug__ else 'warn'))
		
		if isinstance(level, dict):
			level = level.get('level', None)
		
		if level:
			level = level.upper()
			
			config['logging'] = {
					'version': 1,
					'handlers': {
							'console': {
									'class': 'logging.StreamHandler',
									'formatter': 'pretty',
									'level': level,
									'stream': 'ext://sys.stdout',
								}
						},
					'loggers': {
							'web': {
									'level': level,
									'handlers': ['console'],
									'propagate': False,
								},
						},
					'root': {
							'level': level,
							'handlers': ['console']
						},
					'formatters': {
							'pretty': {
									'()': 'web.core.pretty.PrettyFormatter',
								}
						},
				}
			
			basicConfig(level=getattr(logging, level.upper()))
		
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
		
		except Exception as e:
			result = HTTPBadRequest(f"Encountered error de-serializing the request: {context.request!r}")
		
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
		
		if __debug__ and flags.dev_mode:
			e = environ
			cols = __import__('shutil').get_terminal_size().columns
			message = f"{e['REMOTE_ADDR']} \ue0b1 {e['SERVER_PROTOCOL']} \ue0b1 " \
					f"\033[1m{e['REQUEST_METHOD']}\033[0;38;5;232;48;5;255m \ue0b1 " \
					f"\033[4m{e['wsgi.url_scheme']}://{e['SERVER_NAME']}:{e['SERVER_PORT']}" \
					f"{e['SCRIPT_NAME']}{e['PATH_INFO']}" \
					f"{('?' + e['QUERY_STRING']) if e['QUERY_STRING'] else ''}\033[24m"
			rmessage = ""
			
			if e.get('CONTENT_LENGTH', 0):  # If data was submitted as the body, announce what and how large.
				mime = e.get('CONTENT_TYPE', '')
				prefix, _, _ = mime.partition('/')
				if mime:
					icon = MIME_ICON.get(mime, None)
					if not icon: icon = MIME_ICON.get(prefix, MIME_ICON['unknown'])
					rmessage = f"\ue0b1 {mime} {icon} {e.get('CONTENT_LENGTH', 0)} "
			
			kinds = e.get('HTTP_ACCEPT', '*/*').split(',')
			rmessage += f"\ue0b1 {kinds[0]}{'' if len(kinds) == 1 else ', …'}{', */*' if len(kinds) > 1 and '*/*' in e.get('HTTP_ACCEPT', '*/*') else ''} \ue0b1 {e.get('HTTP_ACCEPT_LANGUAGE', '*-*')} "
			
			# print("\033[2J\033[;H\033[0m", end="")
			print(f"\033[38;5;232;48;5;255m {message} {' ' * (cols - len(message) - len(rmessage) - 6 + 39)}{rmessage}\033[m")
		
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
			self._log.debug("Response populated by view.", extra=dict(
					request = id(context),
					view = repr(view),
				))
		
		for ext in signals.after: ext(context)
		
		def capture_done(response: WSGIResponse) -> WSGIResponse:
			yield from response
			for ext in signals.done: ext(context)
		
		if __debug__ and flags.dev_mode:
			e = environ
			cols = __import__('shutil').get_terminal_size().columns
			status, _, message = context.response.status.partition(' ')
			colour = {'2': '150', '3': '111', '4': '214', '5': '166'}[context.response.status[0]]
			message = f"{e['REMOTE_ADDR']} \ue0b3 \033[1m{status} {message}\033[0;38;5;232;48;5;{colour}m"
			rmessage = ""
			
			if context.response.content_length:
				mime = context.response.content_type
				prefix, _, _ = mime.partition('/')
				if mime:
					icon = MIME_ICON.get(mime, None)
					if not icon: icon = MIME_ICON.get(prefix, MIME_ICON['unknown'])
					rmessage = f"{mime} {icon} {context.response.content_length} "
			elif context.response.status[0] == '3':
				message += f" ⤺ {context.response.location} "
			
			# print("\033[2J\033[;H\033[0m", end="")
			print(f"\033[0;38;5;232;48;5;{colour}m {message}\033[0;38;5;232;48;5;{colour}m" \
					f"{' ' * (cols - len(message) - len(rmessage) + 23)}\ue0b3 {rmessage}\033[m")
		
		# This is really long due to the fact we don't want to capture the response too early.
		# We need anything up to this point to be able to simply replace `context.response` if needed.
		return capture_done(context.response.conditional_response_app(environ, start_response))
