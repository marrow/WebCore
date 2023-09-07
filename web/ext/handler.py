"""Permit the specification of internal routes to utilize to replace responses having specific statuses.

This is typically used to implement error page responses using internal redirection. The initially returned status
code is utilized for the ultimate response, so no need to worry that your error page handlers also utilize the error
status.

Example usage, imperative configuration as WSGI middleware: (ignoring that this is a WebCore extension)

	ext = StatusHandlers()
	ext[404] = '/fourohfour'
	ext[HTTPInternalServerError] = '/died'
	app = ext(None, app)  # This extension does not utilize the first argument, an application context.

Immediate declarative, rather than imperative configuration:

	ext = StatusHandlers({
			404: '/fourohfour',
			HTTPInternalServerError: '/died',
		})

"""

from os import environ, getenv as env
from typing import Mapping, Optional, Union
from warnings import warn

from typeguard import typechecked
from webob import Request
from webob.exc import HTTPError

from web.core.typing import Context, PathLike, StatusLike, \
		WSGI, WSGIEnvironment, WSGIStartResponse, WSGIStatus, WSGIHeaders, WSGIException, WSGIWriter


class StatusHandlers:
	handlers: Mapping[int, str]
	
	def __init__(self, handlers:Optional[Mapping[StatusLike, PathLike]]=None):
		self.handlers = {self._normalize(k): str(v) for k, v in handlers.items()} if handlers else {}
	
	@typechecked
	def _normalize(self, status:Union[str, StatusLike]) -> int:
		if isinstance(status, str): status = int(status.partition(' ')[0])))  # Handle strings like "404 Not Found".
		else: status = getattr(status, 'status_int', getattr(status, 'code', status))  # Process everything else.
		
		if not isinstance(status, int):
			raise TypeError(f"Status must be an integer, integer-prefixed string, Response-, or HTTPException-compatible type, not: {status!r} ({type(status)})")
		
		return status
	
	@property
	@typechecked
	def _maintenance(self) -> bool:
		"""Identify if the application is running in "maintenance mode".
		
		"Maintenance mode" will always show the result of the 503 error handler.
		"""
		
		# Pull the maintenance status from the application environment, by default, excluding local development.
		return bool(env('MAINTENANCE', False)) and not __debug__
	
	# Proxy dictionary-like access through to the underlying status code mapping, normalizing on integer keys.
	# These primarily exist to perform automatic extraction of the integer status code from HTTPError subclasses.
	
	@typechecked
	def __contains__(self, status:StatusLike) -> bool:
		"""Determine if an internal redirection has been specified for the given status."""
		status = self._normalize(status)
		return status in self.handlers
	
	@typechecked
	def __getitem__(self, status:StatusLike) -> str:
		"""Retrieve the path specified for handling a specific status code or HTTPException."""
		return self.handlers[status]
	
	@typechecked
	def __setitem__(self, status:StatusLike, handler:PathLike) -> None:
		"""Assign a new handler path for the given status code or HTTPException."""
		status = self._normalize(status)
		self.handlers[status] = str(handler)
	
	@typechecked
	def __delitem__(self, status:StatusLike) -> None:
		"""Remove a handler for the specified status code or HTTPException."""
		status = self._normalize(status)
		del self.handlers[status]
	
	@typechecked
	def __len__(self) -> int:
		"""Return the count of defined status handlers."""
		return len(self.handlers)
	
	# WebCore extension WSGI middleware hook.
	
	@typechecked
	def __call__(self, context:Context, app:WSGI) -> WSGI:
		"""Decorate the WebCore application object with middleware to interpose and internally redirect by status.
		
		This can be directly invoked to wrap any WSGI application, even non-WebCore ones.
		"""
		
		@typechecked
		def middleware(environ:WSGIEnvironment, start_response:WSGIStartResponse) -> WSGIResponse:
			"""Interposing WSGI middleware to capture start_response and internally redirect if needed."""
			
			capture = []
			_maintenance: bool = self._maintenance  # Calculate this only once.
			
			if _maintenance and 503 in self.handlers:
				request = Request.blank(self.handlers[503])
				result = request.send(app, catch_exc_info=True)
				start_response(b'503 Service Unavailable', result.headerlist)
				return result.app_iter
			
			elif _maintenance:
				warn("Maintenance mode enabled with no 503 handler available.", RuntimeWarning)
			
			@typechecked
			def local_start_response(status:WSGIStatus, headers:WSGIHeaders, exc_info:WSGIException=None) -> WSGIWriter:
				"""Capture the arguments to start_response, forwarding if not configured to internally redirect."""
				
				status = status if isinstance(status, str) else status.decode('ascii')
				status_code = int(status.partition(' ')[0])
				
				if status_code not in self.handlers:
					return start_response(status, headers)
				
				capture.extend((status, headers, exc_info, self.handlers.get(status_code, None)))
			
			result = app(environ, local_start_response)
			if not capture or not capture[-1]: return result
			
			request = Request.blank(capture[-1])
			result = request.send(app, catch_exc_info=True)
			
			start_response(capture[0], result.headerlist)
			return result.app_iter
		
		return middleware

