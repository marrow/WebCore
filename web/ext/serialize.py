# encoding: utf-8

"""An example, though quite usable extension to handle list and dictionary return values."""

from __future__ import unicode_literals

from abc import ABCMeta
from collections import Mapping
from inspect import isroutine
from pkg_resources import DistributionNotFound

from marrow.package.host import PluginManager


log = __import__('logging').getLogger(__name__)


# A convienent abstract base class (ABC) to indicate an object of your own provides serialization methods.
Serializable = ABCMeta("Serializable", (object, ), {})


class SerializationPlugins(PluginManager):
	def __init__(self, namespace, folders=None):
		self.__dict__['names'] = set()  # Only short names; easily accessible attributes.
		self.__dict__['types'] = set()  # Only mimetypes; accessible via dictionary notation (array subscripting).
		self.__dict__['short'] = dict()  # A mapping of serializer to matching short name, if found.
		super(SerializationPlugins, self).__init__(namespace, folders)
	
	def register(self, name, plugin):
		super(SerializationPlugins, self).register(name, plugin)
		
		if '/' in name:
			self.types.add(name)
		else:
			self.names.add(name)
			self.short[plugin] = name
	
	def _register(self, dist):
		try:
			super(SerializationPlugins, self)._register(dist)
		except DistributionNotFound:
			pass


class SerializationExtension(object):
	"""A view registry extension for pluggable serialization mechanisms.
	
	You can register new serializers by name and/or mimetype, preferably both. Use the `register` method in an
	application extension, or centrally register your handlers for on-demand loading and easy discovery.
	
	Using explicit registration in an extension would look something like this:
	
		class MyAppExtension:
			needs = {'serialization'}
			
			def start(self, context):
				context.serialize.register('frob', self.frob_dumps)
				context.serialize.register('application/x-frob', self.frob_dumps)
			
			def frob_dumps(self, obj):
				return repr(obj)
	
	Within your `setup.py` metadata, it'd look like:
	
		from setuptools import setup
		
		setup(
			...,
			
			entry_points = {
				'web.serialize': [
					'name = module.import.path:dumps',
					'mime/type = module.import.path:dumps'
				]
			}
		)
	
	When producing endpoints you can return any type registered with this extension to have it automatically
	serialized into a format that is requested, or the default. Out of the box this means that returning lists and
	dictionaries from endpoints will result in JSON serialized data:
	
		def endpoint(context):
			return {'success': True}  # Yay!
	
	This requires that the object you return be passable to the serializer, which can raise issues. You can gain
	control over the exact value or representation passed through to the serializer by defining methods that match the
	short name of the serializer. These may be no-argument methods or `@property` accessors:
	
		class RNG:
			def __json__(self):
				return {'roll': 7}  # is best random no.
			
			@property
			def as_yaml(self):
				return 15  # as determined by d20
	"""
	
	provides = {'serialization'}
	extensions = {'web.serializer'}
	context = {'serialize'}
	
	def __init__(self, default='application/json', types=(list, Mapping, Serializable), methods=True):
		"""Initialize a new instance of this extension.
		
		Unless overridden the serialization view is registered against the `list` and `Mapping` types.
		
		When in doubt, the default serialization mechanism will be used for instances of the given Python types or
		objects matching metaclass types. It is encouraged to define the allowed set of types only once, at
		initialization time. (No effort has been made to make this value easy to find or update during the request
		cycle.)
		
		By default methods will be searched if the requested mimetype has a matching shortened abbreviation, with
		several variations attempted. Initially, double underscore wrapped versions are called, with `as_` prefixed
		versions attempted; if the attribute is callable, it will be called, otherwise the value will be used
		directly.
		
		For improved security disable method search and use only your own classes and forbid the default types which
		may match objects too broadly.
		
		After retrieving some form of serialization result, a handling view is resolved again to correctly populate
		the response while allowing rich serialization formats or streaming serialization.
		"""
		
		self.default = default  # Default mimetype to use if no other match found.
		self.methods = methods  # Search for `__{name}__` and `as_{name}` attributes/methods.
		self.types = types  # Types to register the serialization view for.
		
		# Prepare the plugin registry now; we may need it on start.
		self.manager = SerializationPlugins('web.serialize')
		self.manager.__dict__['__isabstractmethod__'] = False
	
	def start(self, context):
		"""Associate the serialization manager with the context and register views."""
		
		if __debug__:
			log.debug("Registering serialization return value handlers.")
		
		# Bind the default serializer by aliased name.
		self.manager['default'] = self.manager[self.default]
		
		# Bind the plugin manager to the application context.
		context.serialize = self.manager
		
		# Register the serialization views for requested types.
		for kind in self.types:
			context.view.register(kind, self.render_serialization)
	
	def render_serialization(self, context, result):
		"""Render serialized responses."""
		
		serial = context.serialize  # Local scope abbreviation.
		
		# Perform initial mimetype matching and serializer identification.
		match = context.request.accept.best_match(serial.types, default_match=self.default)
		plugin = serial[match]
		short = serial.short.get(plugin, None)
		
		if self.methods and short:
			if hasattr(result, '__' + short + '__'):
				result = getattr(result, '__' + short + '__')
			elif hasattr(result, 'as_' + short):
				result = getattr(result, 'as_' + short)
			
			if isroutine(result):
				result = result()
		
		if __debug__:
			log.debug("Serializing response: " + match)
		
		result = plugin(result)
		
		# Identify a view capable of handling the serialized result.
		for view in context.view(result):
			if view(context, result): break
		else:
			raise TypeError("No view could be found to handle serialized result: " + repr(type(result)))
		
		return True

