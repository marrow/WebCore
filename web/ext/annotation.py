"""Python 3 function annotation typecasting support."""

import typing
from collections import abc
from re import compile as regex
from io import StringIO

from inspect import ismethod, getfullargspec

from ..core.typing import Any, Callable, Context, Dict, Mapping, Tags, List, Optional


SPLIT = lambda v: ",".split(v) if isinstance(v, str) else list(v)


AnnotationAliases = Mapping[type, type]
Mapper = Callable[[str], Any]
AnnotationMappers = Mapping[type, Mapper]


# Helpers utilized in the aliases and mappings below.

def die(type):
	"""Handle the given ABC or typing hint by exploding."""
	
	def inner(value):
		raise TypeError(f"Can not cast to {type!r}, concrete simple type references are preferred.")
	
	return inner

def _nop(value):
	"""A no-operation identity transformation if the abstract type implies or is satisfied by Unicode text.
	
	Use of this indicates a Unicode string is a suitable member of that abstract set.
	"""
	
	return value


# Typecasting assistance.

def to_bytes(value:str) -> bytes:
	return value.encode('utf8') if isinstance(value, str) else bytes(value),


# Many type annotations are "abstract", so we map them to "concrete" types to permit casting on ingress.

aliases:AnnotationAliases = {
		# Core datatypes which may require some assistance to translate from the web.
		bytes: to_bytes,
		
		# Map abstract base classes to their constructors.
		abc.ByteString: bytes,
		abc.Container: _nop,
		abc.Hashable: _nop,
		abc.Iterable: _nop,
		abc.Iterator: iter,
		abc.Mapping: dict,
		abc.MutableMapping: dict,
		abc.Reversible: _nop,
		abc.Sequence: _nop,
		abc.Set: set,
		abc.Sized: _nop,
		
		# "Shallow" pseudo-types mapped to explosions, real types, or casting callables.
		typing.Any: _nop,
		typing.AnyStr: lambda v: str(v),
		typing.AsyncContextManager: die(typing.AsyncContextManager),
		typing.AsyncGenerator: die(typing.AsyncGenerator),
		typing.AsyncIterable: die(typing.AsyncIterable),
		typing.AsyncIterator: die(typing.AsyncIterator),
		typing.Awaitable: die(typing.Awaitable),
		typing.ByteString: to_bytes,
		typing.Callable: die(typing.Callable),
		typing.ChainMap: die(typing.ChainMap),
		typing.ClassVar: die(typing.ClassVar),
		typing.ContextManager: die(typing.ContextManager),
		typing.Coroutine: die(typing.Coroutine),
		typing.Counter: die(typing.Counter),
		typing.DefaultDict: die(typing.DefaultDict),
		typing.ForwardRef: die(typing.ForwardRef),
		typing.Generator: die(typing.Generator),
		typing.Generic: die(typing.Generic),
		typing.Hashable: _nop,
		typing.ItemsView: die(typing.ItemsView),  # TODO: dict and call .items()
		typing.Iterator: die(typing.Iterator),  # TODO: automatically call .iter()
		typing.KeysView: die(typing.KeysView),  # TODO: dict and call .keys
		typing.MappingView: die(typing.MappingView),  # TODO: dict and call .values()
		typing.Match: die(typing.Match),
		typing.NamedTuple: die(typing.NamedTuple),
		typing.Reversible: _nop,
		typing.Sized: _nop,
		typing.IO: StringIO,
		typing.SupportsAbs: float,
		typing.SupportsBytes: bytes,
		typing.SupportsFloat: float,
		typing.SupportsInt: int,
		typing.SupportsRound: float,
		typing.Pattern: regex,
		
		# Potentially nested / recursive / "complex" pseudo-types.
		typing.AbstractSet: set,
		typing.Collection: die(typing.Collection),
		typing.Container: die(typing.Container),
		typing.OrderedDict: dict,
		typing.FrozenSet: frozenset,
		typing.Iterable: _nop,
		typing.List: list,
		typing.Sequence: _nop,
		typing.Mapping: dict,
		typing.MutableMapping: dict,
		typing.MutableSequence: list,
		typing.MutableSet: set,
		typing.Optional: die(typing.Optional),  # TODO: SPECIAL CASE TO UNPACK
		typing.Set: set,
		typing.Tuple: die(typing.Tuple),  # TODO: Container with possible nested types.
		
		# typing.: die(typing.),
	}

mapper:AnnotationMappers = {  # Mechanisms to produce the desired type from basic Unicode text input.
		list: lambda v: v.split(",") if isinstance(v, str) else list(v),
		set: lambda v: v.split(",") if isinstance(v, str) else set(v),
		# dict: ...
	}
















class AnnotationExtension:
	"""Utilize Python 3 function annotations as a method to filter arguments coming in from the web.
	
	Argument annotations are treated as callbacks to execute, passing in the Unicode value coming in from the web and
	swapping it with the value returned by the callback. This allows for trivial typecasting to most built-in Python
	types such as `int`, `float`, etc., as well as creative use such as `','.split` to automatically split a comma-
	separated value. One can of course also write custom callbacks.
	
	For example:
	
		def multiply(a: int, b: int):
			return str(a * b)
	
	This extension also performs a utility wrapping of returned values in the form of a 2-tuple of the return
	annotation itself and the value returned by the callable endpoint. This integrates well with the view registered
	by the `web.template` package to define a template at the head of the function, returning data for the template
	to consume:
	
		def hello(name="world") -> 'mako:hello.html':
			return dict(name=name)
	
	If your editor has difficulty syntax highlighting such annotations, check for a Python 3 compatible update to your
	editor's syntax definitions.
	"""
	
	# Related:
	# https://github.com/aldebaran/strong_typing/tree/master/strong_typing
	# https://pypi.org/project/safe-cast/ (unmaintained) + https://github.com/StasTune/safe-cast
	
	provides:Tags = {'annotation', 'cast', 'typecast'}  # Export these symbols for other extensions to depend upon.
	
	# Execute the following and prune:
	# {n: k.__origin__ for n, k in ((n, getattr(typing, n)) for n in dir(typing) if not n.startswith('_')) \
	# if hasattr(k, '__origin__') and not inspect.isabstract(k.__origin__)}
	
	
	def __init__(self, aliases:Optional[AnnotationAliases]=None, mapper:Optional[AnnotationMappers]=None) -> None:
		"""Initialize the function annotation extension.
		
		You may pass in instance additions and overrides for the type aliases and type mappers if custom behavior is
		desired.
		"""
		super().__init__()
		
		if aliases: self.aliases = {**self.aliases, **aliases}
		if mapper: self.mapper = {**self.mapper, **mapper}
	
	def collect(self, context:Context, handler:Callable, args:List, kw:Dict[str,Any]) -> None:
		"""Inspect and potentially mutate the arguments to the handler.
		
		The args list and kw dictionary may be freely modified, though invalid arguments to the handler will fail.
		"""
		
		spec = getfullargspec(handler)
		arguments = list(spec.args)
		if ismethod(handler): del arguments[0]  # Automatically remove `self` arguments from consideration.
		
		def cast(key, annotation, value):
			"""Attempt to typecast data incoming from the web."""
			
			annotation = self.aliases.get(annotation, annotation)
			if isinstance(annotation, type) and isinstance(value, annotation): return value  # Nothing to do.
			annotation = self.mapper.get(annotation, annotation)
			
			try:
				value = annotation(value)
			except (ValueError, TypeError) as e:
				raise HTTPBadRequest(f"{e.__class__.__name__}: {e} while processing endpoint argument '{arg}'")
			
			return value
		
		# Process positional arguments.
		for i, (key, annotation, value) in enumerate((k, spec.annotations.get(k), v) for k, v in zip(arguments, args)):
			if not annotation: continue  # Skip right past non-annotated arguments.
			args[i] = cast(key, annotation, value)
		
		# Process keyword arguments.
		for key, annotation, value in ((k, spec.annotations.get(k), v) for k, v in kw.items()):
			if not annotation: continue  # Skip right past non-annotated arguments.
			kw[key] = cast(key, annotation, value)
	
	def transform(self, context:Context, handler:Callable, result:Any):
		"""Transform the value returned by the controller endpoint, or transform the result into a 2-tuple.
		
		If the annotation is callable, run the result through the annotation, returning the result. Otherwise,
		transform into 2-tuple of:
		
			(return_annotation, result)
		
		This is a common pattern for recognition and matching by certain views, such as general templating.
		"""
		
		handler = handler.__func__ if hasattr(handler, '__func__') else handler
		annotation = getattr(handler, '__annotations__', {}).get('return', None)
		if not annotation: return result
		
		if callable(annotation):
			return annotation(result)
		
		return (annotation, result)
