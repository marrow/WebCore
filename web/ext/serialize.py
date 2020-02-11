"""An example, though quite usable extension to handle list and dictionary return values."""

from pkg_resources import Distribution, DistributionNotFound
from collections import Mapping as MappingABC, Iterable as IterableABC

from webob.exc import HTTPNotAcceptable
from marrow.package.host import PluginManager

from ..core.typing import Any, Optional, Iterable, Context
from .args import ArgumentExtension

try:
	from bson import json_util as json
except ImportError:
	import json


log = __import__('logging').getLogger(__name__)
json  # Satisfy linter.


class SerializationPlugins(PluginManager):
	def __init__(self, namespace:str, folders:Optional[Iterable[str]]=None) -> None:
		super().__init__(namespace, folders)
		
		self.__dict__['names'] = set()
		self.__dict__['types'] = set()
	
	def register(self, name:str, plugin:Any) -> None:
		super().register(name, plugin)
		
		self.names.add(name)
		if '/' in name: self.types.add(name)
	
	def _register(self, dist:Distribution) -> None:
		try:  # Squelch the exception by simply not registering the plugin if dependencies are missing.
			super()._register(dist)
		except DistributionNotFound:
			pass


class SerializationExtension(ArgumentExtension):
	"""Sample extension demonstrating integration of automatic bidirectional serialization, such as JSON.
	
	This extension registers handlers for lists and dictionaries (technically list and mappings).
	
	Additional serializers can be registered during runtime by other extensions by adding a new mimetype mapping
	to the `context.serialize` dictionary-like object.  For convenience the default serializers are also provided
	using their simple names, so you can access the JSON encoder directly, for example:
	
		context.serialize.json.dumps(...)
	"""
	
	provides: Tags = {'serialization'}
	extensions: Tags = {'web.serializer'}
	context: Tags = {'serialize'}
	
	def __init__(self, default:str='application/json', types:SerializationTypes=(list, MappingABC)) -> None:
		super().__init__()
		
		self.default = default
		self.types = types
	
	def start(self, context:Context) -> None:
		if __debug__:
			log.debug("Registering serialization return value handlers.")
		
		manager = SerializationPlugins('web.serialize')
		manager.__dict__['__isabstractmethod__'] = False  # Resolve Python 2.6+ issue.
		
		context.serialize = manager
		
		# Register the serialization views supported by this extension.
		for kind in self.types:
			context.view.register(kind, self.render_serialization)
	
	
	def render_serialization(self, context:Context, result:Any) -> bool:
		"""Render serialized responses."""
		
		resp = context.response
		serial = context.serialize
		match = context.request.accept.best_match(serial.types, default_match=self.default)
		
		if match is None:
			context.response = HTTPNotAcceptable("\n".join(i for i in serial.types if '/' in i))
			return True
		
		dumps = serial[match]
		result = dumps(result)
		resp.content_type = match
		
		if isinstance(result, bytes):
			resp.body = result
		else:
			resp.charset = 'utf-8'
			resp.text = result
		
		return True
