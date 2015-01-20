# encoding: utf-8

from mimetypes import init, add_type
from webob import Request, Response

from ...core.response import registry
from .helpers import URLGenerator
from web.ext.base import handler


class BaseExtension(object):
	first = True
	always = True
	provides = ["request", "response"]

	def __call__(self, context, app):
		#context.log.name('web.app').debug("Preparing WSGI middleware stack.")
		context.log.debug("Preparing WSGI middleware stack.")
		return app

	def start(self, context):
		#context.log.name('web.app').debug("Registering core return value handlers.")
		context.log.debug("Registering core return value handlers.")
		
		init()
		add_type('text/x-yaml', 'yml')
		add_type('text/x-yaml', 'yaml')
		
		# Register the default return handlers.
		for h in handler.__all__:
			h = getattr(handler, h)
			registry.register(h, *h.types)

	def prepare(self, context):
		"""Add the usual suspects to the context.

		The following are provided by the underlying application:

		* app -- the composed WSGI application
		* root -- the root controller object
		* config -- the complete configuration bunch
		* environ -- the current request environment
		"""

		#context.log.name('ext.base').debug("Preparing the request context.")
		context.log.debug("Preparing the request context.")

		context.request = Request(context.environ)
		context.response = Response(request=context.request)

		context.environ['web.base'] = context.request.script_name
		
		context.request.remainder = context.request.path_info.split('/')

		context.url = URLGenerator(context)
		context.path = []
		# context.log = context.log.name('request').data(request=context.request)

	def dispatch(self, context, consumed, handler, is_endpoint):
		"""Called as dispatch descends into a tier.

		The base extension uses this to maintain the "current url".
		"""
		
		request = context.request
		#context.log.name('ext.base').data(consumed=consumed, handler=handler, endpoint=is_endpoint).debug("Handling dispatch.")
		context.log.debug("Handling dispatch.")
		
		for element in consumed:
			if element == context.request.path_info_peek():
				context.request.path_info_pop()
		
		context.path.append((handler, request.script_name))
		request.remainder = request.remainder[len(consumed):]

		if not is_endpoint:
			context.environ['web.controller'] = str(context.request.script_name)
