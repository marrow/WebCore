# encoding: utf-8

"""An example, though quite usable extension to handle list and dictionary return values."""

# ## Imports

from __future__ import unicode_literals

import json

from collections import Mapping

from web.core.context import Context

try:
	import yaml
except ImportError:
	yaml = None

try:
	from web.template.serialize import bencode
except ImportError:
	bencode = None


# ## Module Globals

log = __import__('logging').getLogger(__name__)


# ## Extension

class SerializationExtension(object):
	"""Sample extension demonstrating integration of automatic serialization, such as JSON.
	
	This extension registers handlers for lists and dictionaries (technically list and mappings).
	
	Additional serializers can be registered during runtime by other extensions by adding a new mimetype mapping
	to the `context.serializer` dictionary-like object.  For convienence the default serializers are also provided
	using their simple names, so you can access the JSON encoder directly, for example:
	
		context.serializer.json.dumps(...)
	"""
	
	provides = {'serialization', 'json'}
	
	def __init__(self):
		self.provides = set(self.provides)  # We conditionally add the other options.
		self.mapping = {'json': json, 'application/json': json}  # Always present.
		
		if yaml:
			self.mapping['application/x-yaml'] = self.mapping['yaml'] = yaml
			self.provides.add('yaml')
		
		if bencode:
			self.mapping['application/x-bencode'] = self.mapping['bencode'] = bencode
			self.provides.add('bencode')
	
	# ### Application-Level Callbacks
	
	def start(self, context):
		if __debug__:
			log.debug("Registering serialization return value handlers.")
		
		context.serializer = Context(self.mapping)
		
		# Register the core views supported by the base framework.
		context.view.register(list, self.render_serialization)
		context.view.register(Mapping, self.render_serialization)
	
	# ### Views
	
	def render_serialization(self, context, result):
		"""Render serialized responses."""
		
		resp = context.response
		serial = context.serializer
		match = context.request.accept.best_match(serial.keys(), default_match='application/json')
		
		resp.charset = 'utf-8'
		resp.text = serial[match].dumps(result)
		
		return True

