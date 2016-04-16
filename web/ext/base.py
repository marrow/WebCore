# encoding: utf-8

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
from webob import Request, Response

from web.core.compat import str, unicode
from web.core.util import safe_name

log = __import__('logging').getLogger(__name__)


class BaseExtension(object):
	first = True
	always = True
	provides = ["base", "request", "response"]

	def start(self, context):
		if __debug__:
			log.debug("Registering core return value handlers.")
		
		init()
		add_type('text/x-yaml', 'yml')
		add_type('text/x-yaml', 'yaml')
		
		register = context.view.register
		
		register(type(None), self.render_none)
		register(Response, self.render_response)
		register(str, self.render_binary)
		register(unicode, self.render_text)
		register(IOBase, self.render_file)
		register(Generator, self.render_generator)
	
	def prepare(self, context):
		"""Add the usual suspects to the context.

		The following are provided by the underlying application:

		* app -- the composed WSGI application
		* root -- the root controller object
		* config -- the complete configuration bunch
		* environ -- the current request environment
		"""

		if __debug__:
			log.debug("Preparing request context.")

		context.request = Request(context.environ)
		context.response = Response(request=context.request)

		context.environ['web.base'] = context.request.script_name
		
		context.request.remainder = context.request.path_info.split('/')
		if context.request.remainder and not context.request.remainder[0]:
			del context.request.remainder[0]

		context.path = []
	
	def dispatch(self, context, consumed, handler, is_endpoint):
		"""Called as dispatch descends into a tier.

		The base extension uses this to maintain the "current url".
		"""
		
		request = context.request
		
		if __debug__:
			log.debug("Handling dispatch event.", extra=dict(consumed=consumed, handler=safe_name(handler), endpoint=is_endpoint))
		
		if not consumed and context.request.path_info_peek() == '':
			consumed = ['']
		
		if consumed:
			if not isinstance(consumed, (list, tuple)):
				consumed = consumed.split('/')
			
			for element in consumed:
				if element == context.request.path_info_peek():
					context.request.path_info_pop()
		
		context.path.append((handler, request.script_name))
		
		if consumed:
			request.remainder = request.remainder[len(consumed):]
	
	def render_none(self, context, result):
		context.response.length = 0
		context.response.body = b''
		return True
	
	def render_response(self, context, result):
		context.response = result
		return True
	
	def render_binary(self, context, result):
		context.response.app_iter = iter((result, ))
		return True
	
	def render_text(self, context, result):
		context.response.text = result
		return True
	
	def render_file(self, context, result):
		if __debug__:
			log.debug("Processing file-like object.", extra=dict(request=id(context), result=repr(result)))
		
		response = context.response = Response(
				conditional_response = True,
			)
		
		modified = mktime(gmtime(getmtime(result.name)))
		
		response.last_modified = datetime.fromtimestamp(modified)
		response.cache_control = 'public'
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
		context.response.encoding = 'utf8'
		context.response.app_iter = (
				(i.encode('utf8') if isinstance(i, unicode) else i)
				for i in result if i is not None
			)
		return True

