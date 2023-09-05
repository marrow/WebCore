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
from urllib.parse import unquote_plus
from typing import Mapping, Optional, Union

from webob import Request, Response
from webob.exc import HTTPError

from web.core.typing import Context, \
		WSGI, WSGIEnvironment, WSGIStartResponse, WSGIStatus, WSGIHeaders, WSGIException, WSGIWriter


StatusLike = Union[int, Response, HTTPError]


class StatusHandlers:
	handlers: Mapping[int, str]
	
	def __init__(self, handlers:Optional[Mapping[int, str]]=None):
		self.handlers = handlers or {}
	
	def _normalize(self, status:StatusLike) -> int:
		status = getattr(status, 'status_int', getattr(status, 'code', status))
		if not isinstance(status, int): raise TypeError("HTTP status code must be an integer, Response-, or HTTPException-compatible type.")
		return status
	
	@property
	def _maintenance(self) -> bool:
		"""Identify if the application is running in "maintenance mode".
		
		"Maintenance mode" will always show the result of the 503 error handler.
		"""
		
		# Pull the maintenance status from the application environment, by default, excluding local development.
		return bool(env('MAINTENANCE', False)) and not __debug__
	
	# Proxy dictionary-like access through to the underlying status code mapping, normalizing on integer keys.
	
	def __getitem__(self, status:StatusLike) -> str:
		"""Retrieve the path specified for handling a specific status code or HTTPException."""
		return self.handlers[status]
	
	def __setitem__(self, status:StatusLike, handler:str) -> None:
		"""Assign a new handler path for the given status code or HTTPException."""
		status = self._normalize(status)
		self.handlers[status] = handler
	
	def __delitem__(self, status:StatusLike) -> None:
		"""Remove a handler for the specified status code or HTTPException."""
		status = self._normalize(status)
		del self.handlers[status]
	
	# WebCore extension WSGI middleware hook.
	
	def __call__(self, context:Context, app:WSGI) -> WSGI:
		"""Decorate the WebCore application object with middleware to interpose and internally redirect by status."""
		
		def middleware(environ:WSGIEnvironment, start_response:WSGIStartResponse) -> WSGIResponse:
			"""Interposing WSGI middleware to capture start_response and internally redirect if needed."""
			
			capture = []
			
			if self._maintenance:
				request = Request.blank(self.handlers[503])
				result = request.send(app, catch_exc_info=True)
				start_response(b'503 Service Unavailable', result.headerlist)
				return result.app_iter
			
			def local_start_response(status:WSGIStatus, headers:WSGIHeaders, exc_info:WSGIException=None) -> WSGIWriter:
				"""Capture the arguments to start_response, forwarding if not configured to internally redirect."""
				
				status = status if isinstance(status, str) else status.decode('ascii')
				status_code = int(status.partition(' ')[0])
				
				if status_code not in self.handlers:
					return start_response(status, headers)
				
				capture.extend((status, headers, exc_info, self.handlers.get(status_code, None)))
			
			result = app(environ, local_start_response)
			if not capture: return result
			
			request = Request.blank(capture[-1])
			result = request.send(app, catch_exc_info=True)
			
			start_response(capture[0], result.headerlist)
			return result.app_iter
		
		return middleware

