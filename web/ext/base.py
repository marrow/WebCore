"""The base extension providing request, response, and core views."""

from collections import namedtuple
from collections.abc import Generator
from datetime import datetime
from io import IOBase
from mimetypes import init, add_type, guess_type
from os.path import getmtime
from pathlib import PurePosixPath as Path
from time import mktime, gmtime
from webob import Request, Response

from ..core.util import safe_name
from ..core.typing import Any, Context, Response, Tags


# ## Module Globals

log = __import__('logging').getLogger(__name__)


# ## Helper Classes

Crumb = namedtuple('Breadcrumb', ('handler', 'path'))


class Bread(list):
	@property
	def current(self):
		return self[-1].path


# ## Extension

class BaseExtension:
	"""Base framework extension.
	
	This extension is not meant to be manually constructed or manipulated; use is automatic.
	"""
	
	first: bool = True  # Must occur as early as possible in callback lists.
	always: bool = True  # Always enabled.
	provides: Tags = ["base", "request", "response"]  # Export these symbols for use as other extension's dependencies.
	uses: Tags = {'timing.prefix'}
	
	# ### Application-Level Callbacks
	
	def start(self, context:Context) -> None:
		if __debug__: log.debug("Registering core return value handlers.")
		
		# This prepares the mimetypes registry, and adds values typically missing from it.
		init()
		add_type('text/x-yaml', 'yml')
		add_type('text/x-yaml', 'yaml')
		
		# Register the core views supported by the base framework.
		register = context.view.register
		register(type(None), self.render_none)
		register(Response, self.render_response)
		register(bytes, self.render_binary)
		register(str, self.render_text)
		register(IOBase, self.render_file)
		register(Generator, self.render_generator)
	
	# ### Request-Level Callbacks
	
	def prepare(self, context:Context) -> None:
		"""Add the usual suspects to the context.
		
		This adds `request`, `response`, and `path` to the `RequestContext` instance.
		"""
		
		if __debug__: log.debug("Preparing request context.", extra=dict(request=id(context)))
		
		# Bridge in WebOb `Request` and `Response` objects.
		# Extensions shouldn't rely on these, using `environ` where possible instead.
		context.request = Request(context.environ)
		context.response = Response(request=context.request)
		
		# Record the initial path representing the point where a front-end web server bridged to us.
		context.environ['web.base'] = context.request.script_name
		
		# Track the remaining (unprocessed) path elements.
		context.request.remainder = context.request.path_info.split('/')
		if context.request.remainder and not context.request.remainder[0]:
			del context.request.remainder[0]
		
		# Track the "breadcrumb list" of dispatch through distinct controllers.
		context.path = Bread()
	
	def dispatch(self, context:Context, crumb:Crumb) -> None:
		"""Called as dispatch descends into a tier.
		
		The base extension uses this to maintain the "current url".
		"""
		
		request = context.request
		
		if __debug__:
			log.debug("Handling dispatch event.", extra=dict(
					request = id(context),
					consumed = consumed,
					handler = safe_name(handler),
					endpoint = is_endpoint
				))
		
		# The leading path element (leading slash) requires special treatment.
		if not consumed and context.request.path_info_peek() == '':
			consumed = ['']
		
		nConsumed = 0
		if consumed:
			# Migrate path elements consumed from the `PATH_INFO` to `SCRIPT_NAME` WSGI environment variables.
			if not isinstance(consumed, (list, tuple)):
				consumed = consumed.split('/')
			
			for element in consumed:
				if element == context.request.path_info_peek():
					context.request.path_info_pop()
					nConsumed += 1
				else:
					break
		
		# Update the breadcrumb list.
		context.path.append(Crumb(handler, Path(request.script_name)))
		
		if consumed:  # Lastly, update the remaining path element list.
			request.remainder = request.remainder[nConsumed:]
	
	# ### Views
	
	def render_none(self, context:Context, result:None) -> bool:
		"""Render empty responses."""
		
		context.response.body = b''
		del context.response.content_length
		
		return True
	
	def render_response(self, context:Context, result:Response) -> bool:
		"""Allow direct returning of WebOb `Response` instances."""
		
		context.response = result
		
		return True
	
	def render_binary(self, context:Context, result:bytes) -> bool:
		"""Return binary responses unmodified."""
		
		context.response.app_iter = iter((result, ))  # This wraps the binary string in a WSGI body iterable.
		
		return True
	
	def render_text(self, context:Context, result:str) -> bool:
		"""Return textual responses, encoding as needed."""
		
		context.response.text = result
		
		return True
	
	def render_file(self, context:Context, result:IOBase) -> bool:
		"""Perform appropriate metadata wrangling for returned open file handles."""
		
		if __debug__: log.debug("Processing file-like object.", extra=dict(request=id(context), result=repr(result)))
		
		response = context.response
		response.conditional_response = True
		
		modified = mktime(gmtime(getmtime(result.name)))
		
		response.last_modified = datetime.fromtimestamp(modified)
		ct, ce = guess_type(result.name)
		if not ct: ct = 'application/octet-stream'
		response.content_type, response.content_encoding = ct, ce
		response.etag = str(modified)
		
		result.seek(0, 2)  # Seek to the end of the file.
		response.content_length = result.tell()
		
		result.seek(0)  # Seek back to the start of the file.
		response.body_file = result
		
		return True
	
	def render_generator(self, context:Context, result:Generator) -> bool:
		"""Attempt to serve generator responses through stream encoding.
		
		This allows for direct use of cinje template functions, which are generators, as returned views.
		"""
		
		context.response.encoding = 'utf-8'
		context.response.app_iter = (
				(i.encode('utf-8') if isinstance(i, bytes) else str(i))  # Stream encode Unicode chunks.
				for i in result if i is not None  # Skip None values.
			)
		
		return True
