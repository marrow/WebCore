# encoding: utf-8

from __future__ import unicode_literals

from webob.multidict import MultiDict
from marrow.package.canonical import name
from marrow.package.host import PluginManager

from .compat import py3, pypy


log = __import__('logging').getLogger(__name__)


class WebViews(PluginManager):
	"""The WebCore view registry.
	
	WebCore uses a registry of callables to transform values returned by controllers for use as a response. This
	translation process is used to support the built-in types (see the `base` extension) and can be extended by your
	own application to support additional types.  This is effectively the "view" component of Model-View-Controller.
	
	A view handler takes the result of calling a controller endpoint and applies the result to the response. It can be
	as simple as a bare function that accepts the current RequestContext instance and the value returned by the
	endpoint and either returns a truthy value to indicate successful handling, or a falsy value to indicate that this
	view handler could not handle the result. The simplest case is a handler that always "passes the buck" and handles
	nothing:
	
		def ignore(context, result):
			pass
	
	Slightly more useful would be to assign the result directly to the response:
	
		def stringy(context, result):
			context.response.text = result
			return True
	
	As an example pulled from the "template" extension, you can use an "exit early" strategy to selectively handle
	subsets of the type your view is registered against, such as only handling 2-tuples with a specific first value:
	
		from json import dumps
		
		def json(context, result):
			if len(result) != 2 or result[0] != 'json': return
			context.response.text = dumps(result)
	
	A view may go so far as to wholly replace the context.response object; any callable WSGI application can be
	utilized as such. Cooperative response construction is strongly preferred, however.
	
	If you frequently hand back serialized data, you may be able to simplify your controller code and reduce
	boilerplate by simply returning your model instances.  By registering a view handler for your model class you can
	implement the serialization in a single, centralized location, making security and testing much easier.
	
	When a controller raises an HTTPError subclass it is treated as the return value.  As such you can take specific
	action on any given error by registering a view handler for the specific exception subclass (i.e. `HTTPNotFound`),
	such as rendering a pretty error page.  By default these exceptions are treated as a WSGI application and are
	directly used as the response, but only if no more specific handlers are registered.
	"""
	
	__isabstractmethod__ = False  # Work around a Python 3.4+ issue, since our instances are callable.
	
	def __init__(self, ctx):
		"""View registry constructor.
		
		The view registry is not meant to be instantiated by third-party software. Instead, access the registry as
		an attribute of the the current Application or Request context: `context.view`
		"""
		super(WebViews, self).__init__('web.view')
		self.__dict__['_map'] = MultiDict()
	
	def register(self, kind, handler):
		"""Register a handler for a given type, class, interface, or abstract base class.
		
		View registration should happen within the `start` callback of an extension.  For example, to register the
		previous `json` view example:
		
			class JSONExtension:
				def start(self, context):
					context.view.register(tuple, json)
		
		The approach of explicitly referencing a view handler isn't very easy to override without also replacing the
		extension originally adding it, however there is another approach. Using named handlers registered as discrete
		plugins (via the `entry_point` argument in `setup.py`) allows the extension to easily ask "what's my handler":
		
			class JSONExtension:
				def start(self, context):
					context.view.register(tuple, context.view.json)
		
		Otherwise unknown attributes of the view registry will attempt to look up a handler plugin by that name.
		"""
		if __debug__:
			if py3 and not pypy:
				log.debug("Registering view handler.", extra=dict(type=name(kind), handler=name(handler)))
			else:
				log.debug("Registering view handler.", extra=dict(type=repr(kind), handler=repr(handler)))
		
		self._map.add(kind, handler)
		
		return handler
	
	def __call__(self, result):
		"""Identify view to use based on the type of result.
		
		This generates a stream of candidates which should be called in turn until one returns a truthy value.
		"""
		
		kind = type(result)
		
		for kind, candidate in self._map.iteritems():
			if isinstance(result, kind):
				yield candidate

