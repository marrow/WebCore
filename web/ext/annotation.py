"""Python 3 function annotation typecasting support."""

import typing
from collections import abc

from inspect import ismethod, getfullargspec

from ..core.typing import Any, Callable, Mapping, Tags, Optional


SPLIT = lambda v: ",".split(v) if isinstance(v, str) else list(v)


AnnotationAliases = Mapping[type, type]
Mapper = Callable[[str], Any]
AnnotationMappers = Mapping[type, Mapper]


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
	
		def hello(name="world"): -> 'mako:hello.html'
			return dict(name=name)
	
	If your editor has difficulty syntax highlighting such annotations, check for a Python 3 compatible update to your
	editor's syntax definitions.
	"""
	
	provides:Tags = {'annotation', 'cast', 'typecast'}  # Export these symbols for other extensions to depend upon.
	
	# Execute the following and prune:
	# {n: k.__origin__ for n, k in ((n, getattr(typing, n)) for n in dir(typing) if not n.startswith('_')) \
	# if hasattr(k, '__origin__') and not inspect.isabstract(k.__origin__)}
	
	aliases:AnnotationAliases = {  # These type annotations are "abstract", so we map them to "concrete" types for casting.
			abc.ByteString: bytes,
			abc.Iterable: list,
			abc.Mapping: dict,
			abc.MutableMapping: dict,
			typing.AbstractSet: set,
			typing.ByteString: bytes,
			typing.Iterable: list,
			typing.Mapping: dict,
			typing.MutableMapping: dict,
			typing.MutableSequence: list,
			typing.MutableSet: set,
			typing.Sequence: list,
		}
	
	mapper:AnnotationMappers = {  # Mechanisms to produce the desired type from basic Unicode text input.
			list: lambda v: v.split(",") if isinstance(v, str) else list(v),
			set: lambda v: v.split(",") if isinstance(v, str) else set(v),
		}
	
	def __init__(self, aliases:Optional[AnnotationAliases]=None, mapper:Optional[AnnotationMappers]=None):
		"""Initialize the function annotation extension.
		
		You may pass in instance additions and overrides for the type aliases and type mappers if custom behavior is
		desired.
		"""
		super().__init__()
		
		if aliases: self.aliases = {**self.aliases, **aliases}
		if mapper: self.mapper = {**self.mapper, **mapper}
	
	# ### Request-Local Callbacks
	
	def collect(self, context, handler, args, kw):
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
	
	def transform(self, context, handler, result):
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
