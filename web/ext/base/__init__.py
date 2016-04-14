# encoding: utf-8

from mimetypes import init, add_type
from webob import Request, Response

from web.ext.base import handler

if __debug__:
	from marrow.package.canonical import name
	
	try:
		from werkzeug.debug import DebuggedApplication
	except ImportError:
		DebuggedApplication = None


log = __import__('logging').getLogger(__name__)


class BaseExtension(object):
	first = True
	always = True
	provides = ["request", "response"]

	def __call__(self, context, app):
		if __debug__:
			log.debug("Preparing WSGI middleware stack.")
		
		if __debug__ and DebuggedApplication is not None:
			app = DebuggedApplication(app, evalex=True, console_path='/_console')
		
		return app

	def start(self, context):
		#context.log.name('web.app').debug("Registering core return value handlers.")
		if __debug__:
			log.debug("Registering core return value handlers.")
		
		init()
		add_type('text/x-yaml', 'yml')
		add_type('text/x-yaml', 'yaml')
		
		# Register the default return handlers.
		for h in handler.__all__:
			h = getattr(handler, h)
			for kind in h.types:
				context.view.register(kind, h)
	
	def prepare(self, context):
		"""Add the usual suspects to the context.

		The following are provided by the underlying application:

		* app -- the composed WSGI application
		* root -- the root controller object
		* config -- the complete configuration bunch
		* environ -- the current request environment
		"""

		#context.log.name('ext.base').debug("Preparing the request context.")
		if __debug__:
			log.debug("Preparing request context.")

		context.request = Request(context.environ)
		context.response = Response(request=context.request)

		context.environ['web.base'] = context.request.script_name
		
		context.request.remainder = context.request.path_info.split('/')
		if context.request.remainder and not context.request.remainder[0]:
			del context.request.remainder[0]

		# context.url = URLGenerator(context)
		context.path = []
		# log = context.log.name('request').data(request=context.request)
	
	def dispatch(self, context, consumed, handler, is_endpoint):
		"""Called as dispatch descends into a tier.

		The base extension uses this to maintain the "current url".
		"""
		
		request = context.request
		
		if __debug__:
			log.debug("Handling dispatch event.", extra=dict(consumed=consumed, handler=name(handler), endpoint=is_endpoint))
		
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
		
		if not is_endpoint:
			context.environ['web.controller'] = str(context.request.script_name)

