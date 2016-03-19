# encoding: utf-8

"""The WebCore view registry.

WebCore uses a registry of callables to transform values returned by controllers for use as a response. This
translation process is used to support the built-in types (see the `base` extension) and can be extended by your
own application to support additional types.  This is effectively the "view" component of Model-View-Controller.

The `template` extension provides support for template-based views using this mechanism.

## Automatic Transformation of Models

If you frequently hand back serialized data, you may be able to simplify your controller code and reduce boilerplate
by simply returning your model instances.  By registering a response handler for your model class you can implement
the serialization in a single, centralized location, making security and testing much easier.

## Exception Processing

When a controller raises an HTTPError subclass it is treated as the return value.  As such you can take specific
action on any given error, including rendering a pretty error page, etc.  By default these exceptions are treated as
a WSGI application and are executed, but only if no more specific handlers are registered.

Certain extensions, such as the debugging extension, provide their own exception handlers.
"""

from __future__ import unicode_literals

from weakref import ref
from webob.multidict import MultiDict
from marrow.package.canonical import name
from marrow.package.host import PluginManager


log = __import__('logging').getLogger(__name__)


class WebViews(PluginManager):
	__isabstractmethod__ = False
	
	def __init__(self, ctx):
		super(WebViews, self).__init__('web.view')
		
		# Perform the mapping.
		self.__dict__['_map'] = MultiDict()
	
	def register(self, kind, handler):
		log.debug("Registering view handler.", extra=dict(type=name(kind), handler=name(handler)))
		
		self._map.add(kind, handler)
	
	def __call__(self, result):
		"""Identify view to use based on the type of result."""
		
		kind = type(result)
		
		for kind, candidate in self._map.iteritems():
			if isinstance(result, kind):
				yield candidate
