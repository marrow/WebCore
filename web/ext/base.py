# encoding: utf-8

"""The base extension providing request, response, and core views."""

# ## Imports

from __future__ import unicode_literals

from io import IOBase
try:
	IOBase = (IOBase, file)
except:
	pass

try:
	from collections import Generator
except ImportError:
	def _tmp(): yield None  # pragma: no cover
	Generator = type(_tmp())

from os.path import getmtime
from time import mktime, gmtime
from datetime import datetime
from mimetypes import init, add_type, guess_type
from collections import namedtuple
from webob import Request, Response

from web.core.compat import str, unicode, Path
from web.core.util import safe_name


# ## Module Globals

log = __import__('logging').getLogger(__name__)


# ## Helper Classes

Crumb = namedtuple('Breadcrumb', ('handler', 'path'))


class Bread(list):
	@property
	def current(self):
		return self[-1].path



# ## Extension

class BaseExtension(object):
	"""Base framework extension.
	
	This extension is not meant to be manually constructed or manipulated; use is automatic.
	"""
	
	first = True  # Must occur as early as possible in callback lists.
	always = True  # Always enabled.
	provides = ["base", "request", "response"]  # Export these symbols for use as other extension's dependencies.
	
	# ### Application-Level Callbacks
	
	def start(self, context):
		if __debug__:
			log.debug("Registering core return value handlers.")
		
		# This prepares the mimetypes registry, and adds values typically missing from it.
		init()
		add_type('text/x-yaml', 'yml')
		add_type('text/x-yaml', 'yaml')
		
		# Register the core views supported by the base framework.
		register = context.view.register
		register(type(None), self.render_none)
		register(Response, self.render_response)
		register(str, self.render_binary)
		register(unicode, self.render_text)
		register(IOBase, self.render_file)
		register(Generator, self.render_generator)
	
	# ### Request-Level Callbacks
	
	def prepare(self, context):
		"""Add the usual suspects to the context.
		
		This adds `request`, `response`, and `path` to the `RequestContext` instance.
		"""
		
		if __debug__:
			log.debug("Preparing request context.", extra=dict(request=id(context)))
		
		# Bridge in WebOb `Request` and `Response` objects.
		# Extensions shouldn't rely on these, using `environ` where possible instead.
		context.request = Request(context.environ)
		context.response = Response(request=context.request)
		
		# Record the initial path representing the point where a front-end web server bridged to us.
		context.environ['web.base'] = context.request.script_name
		
		# Track the remaining (unprocessed) path elements.
		context.request.remainder = context.request.path_info.strip('/').split('/')
		if context.request.remainder and not context.request.remainder[0]:
			del context.request.remainder[0]
		
		# Track the "breadcrumb list" of dispatch through distinct controllers.
		context.path = Bread()
	
	def dispatch(self, context, consumed, handler, is_endpoint):
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
	
	def render_none(self, context, result):
		"""Render empty responses."""
		context.response.body = b''
		del context.response.content_length
		return True
	
	def render_response(self, context, result):
		"""Allow direct returning of WebOb `Response` instances."""
		context.response = result
		return True
	
	def render_binary(self, context, result):
		"""Return binary responses unmodified."""
		context.response.app_iter = iter((result, ))  # This wraps the binary string in a WSGI body iterable.
		return True
	
	def render_text(self, context, result):
		"""Return textual responses, encoding as needed."""
		context.response.text = result
		return True
	
	def render_file(self, context, result):
		"""Perform appropriate metadata wrangling for returned open file handles."""
		if __debug__:
			log.debug("Processing file-like object.", extra=dict(request=id(context), result=repr(result)))
		
		response = context.response
		response.conditional_response = True
		
		modified = mktime(gmtime(getmtime(result.name)))
		
		response.last_modified = datetime.fromtimestamp(modified)
		ct, ce = guess_type(result.name)
		if not ct: ct = 'application/octet-stream'
		response.content_type, response.content_encoding = ct, ce
		response.etag = unicode(modified)
		
		result.seek(0, 2)  # Seek to the end of the file.
		response.content_length = result.tell()
		
		result.seek(0)  # Seek back to the start of the file.
		response.body_file = result
		
		return True
	
	def render_generator(self, context, result):
		"""Attempt to serve generator responses through stream encoding.
		
		This allows for direct use of cinje template functions, which are generators, as returned views.
		"""
		context.response.encoding = 'utf8'
		context.response.app_iter = (
				(i.encode('utf8') if isinstance(i, unicode) else i)  # Stream encode unicode chunks.
				for i in result if i is not None  # Skip None values.
			)
		return True

