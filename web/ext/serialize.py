"""An example, though quite usable extension to handle list and dictionary return values."""

from pkg_resources import Distribution, DistributionNotFound
from collections.abc import Mapping as MappingABC, Iterable as IterableABC

from webob.exc import HTTPNotAcceptable
from marrow.package.host import PluginManager

from ..core.typing import Any, Callable, Context, Optional, Iterable, Tags, SerializationTypes, PositionalArgs, KeywordArgs, check_argument_types
from .args import ArgumentExtension

try:
	from bson import json_util as json
except ImportError:
	import json


log = __import__('logging').getLogger(__name__)
json  # Satisfy linter.


class SerializationPlugins(PluginManager):
	def __init__(self, namespace:str, folders:Optional[Iterable[str]]=None) -> None:
		assert check_argument_types()
		
		super().__init__(namespace, folders)
		
		self.__dict__['names'] = set()
		self.__dict__['types'] = set()
	
	def register(self, name:str, plugin:Any) -> None:
		assert check_argument_types()
		
		super().register(name, plugin)
		
		self.names.add(name)
		if '/' in name: self.types.add(name)
	
	def _register(self, dist:Distribution) -> None:
		assert check_argument_types()
		
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
	uses: Tags = {'kwargs.get'}  # Request body overrides query string arguments.
	extensions: Tags = {'web.serializer'}
	context: Tags = {'serialize'}
	
	def __init__(self, default:str='application/json', types:SerializationTypes=(list, MappingABC)) -> None:
		super().__init__()
		
		self.default = default
		self.types = types
	
	def start(self, context:Context) -> None:
		assert check_argument_types()
		
		if __debug__:
			log.info("Registering serialization return value handlers.")
		
		manager = SerializationPlugins('web.serialize')
		manager.__dict__['__isabstractmethod__'] = False  # Resolve Python 2.6+ issue.
		
		context.serialize = manager
		
		# Register the serialization views supported by this extension.
		for kind in self.types:
			context.view.register(kind, self.render_serialization)
	
	def collect(self, context:Context, endpoint:Callable, args:PositionalArgs, kw:KeywordArgs) -> None:
		assert check_argument_types()
		
		req: Request = context.request
		mime: str = req.content_type.partition(';')[0]
		
		try:
			loads: Deserializer = context.deserialize[mime]
		except KeyError:
			raise HTTPUnsupportedMediaType("\n".join(i for i in context.deserialize if '/' in i))  # https://httpstatuses.com/415
		
		body = context.request.body
		
		if context.request.charset:  # If the content is textual, e.g. JSON...
			body = body.decode(req.charset)  # ... decode the binary to a Unicode string.
		
		try:  # Attempt deserialization using the matched deserialization callable.
			body = loads(body)
		except Exception as e:  # Mechanically unable to process incoming data. ("malformed request syntax")
			raise HTTPBadRequest(str(e))  # https://httpstatuses.com/400
		
		if isinstance(body, MappingABC):  # E.g. JSON Object, YAML document, ...
			self._process_rich_kwargs(body, kw)
		elif isinstance(body, IterableABC):  # E.g. multi-record YAML, JSON Array, ...
			args.extend(body)
		else:  # Incoming data was mechanically valid, but unprocessable.
			raise HTTPUnprocessableEntity("Must represent a mapping or iterable.")  # https://httpstatuses.com/422
	
	def render_serialization(self, context:Context, result:Any) -> bool:
		"""Render serialized responses."""
		
		assert check_argument_types()
		
		resp = context.response
		serial = context.serialize
		match = context.request.accept.best_match(serial.types, default_match=self.default)
		
		if match is None:
			context.response = HTTPNotAcceptable("\n".join(i for i in serial.types if '/' in i))
			return True
		
		dumps = serial[match]
		result = dumps(result)
		if not resp.content_type: resp.content_type = match
		
		if isinstance(result, bytes):
			resp.body = result
		else:
			resp.charset = 'utf-8'
			resp.text = result
		
		return True
