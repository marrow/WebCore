# encoding: utf-8

"""An example, though quite usable extension to handle list and dictionary return values."""

# ## Imports

from __future__ import unicode_literals

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
		
		manager = PluginManager('web.serialize')
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
		match = context.request.accept.best_match(serial, default_match=self.default)
		result = serial[match](result)
		
		if isinstance(result, str):
			result = result.decode('utf-8')
		
		resp.charset = 'utf-8'
		resp.content_type = match
		resp.text = result
		
		return True

