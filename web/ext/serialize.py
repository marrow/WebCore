# encoding: utf-8

"""An example, though quite usable extension to handle list and dictionary return values."""

# ## Imports

from __future__ import unicode_literals

import pkg_resources
from collections import Mapping

from marrow.package.host import PluginManager
from web.core.compat import str


try:
	from bson import json_util as json
except ImportError:
	import json


# ## Module Globals

log = __import__('logging').getLogger(__name__)
json  # Satisfy linter.


# ## Plugin Management


class SerializationPlugins(PluginManager):
	def __init__(self, namespace, folders=None):
		self.__dict__['names'] = set()
		self.__dict__['types'] = set()
		super(SerializationPlugins, self).__init__(namespace, folders)
	
	def register(self, name, plugin):
		super(SerializationPlugins, self).register(name, plugin)
		
		self.names.add(name)
		
		if '/' in name:
			self.types.add(name)
	
	def _register(self, dist):
		try:
			super(SerializationPlugins, self)._register(dist)
		except pkg_resources.DistributionNotFound:
			pass


# ## Extension

class SerializationExtension(object):
	"""Sample extension demonstrating integration of automatic serialization, such as JSON.
	
	This extension registers handlers for lists and dictionaries (technically list and mappings).
	
	Additional serializers can be registered during runtime by other extensions by adding a new mimetype mapping
	to the `context.serialize` dictionary-like object.  For convienence the default serializers are also provided
	using their simple names, so you can access the JSON encoder directly, for example:
	
		context.serialize.json.dumps(...)
	"""
	
	provides = {'serialization'}
	extensions = {'web.serializer'}
	context = {'serialize'}
	
	def __init__(self, default='application/json', types=(list, Mapping)):
		self.default = default
		self.types = types
	
	# ### Application-Level Callbacks
	
	def start(self, context):
		if __debug__:
			log.debug("Registering serialization return value handlers.")
		
		manager = SerializationPlugins('web.serialize')
		manager.__dict__['__isabstractmethod__'] = False
		
		context.serialize = manager
		
		# Register the serialization views supported by this extension.
		for kind in self.types:
			context.view.register(kind, self.render_serialization)
	
	# ### Views
	
	def render_serialization(self, context, result):
		"""Render serialized responses."""
		
		resp = context.response
		serial = context.serialize
		match = context.request.accept.best_match(serial.types, default_match=self.default)
		result = serial[match](result)
		
		if isinstance(result, str):
			result = result.decode('utf-8')
		
		resp.charset = 'utf-8'
		resp.content_type = match
		resp.text = result
		
		return True

