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
	
	
	# ### Request-Local Callbacks
	
	def mutate(self, context, handler, args, kw):
		"""Inspect and potentially mutate the given handler's arguments.
		
		The args list and kw dictionary may be freely modified, though invalid arguments to the handler will fail.
		"""
		def cast(arg, val):
			if arg not in annotations:
				return
			
			cast = annotations[key]
			
			try:
				val = cast(val)
			except (ValueError, TypeError) as e:
				parts = list(e.args)
				parts[0] = parts[0] + " processing argument '{}'".format(arg)
				e.args = tuple(parts)
				raise
			
			return val
			
		annotations = getattr(handler.__func__ if hasattr(handler, '__func__') else handler, '__annotations__', None)
		if not annotations:
			return
		
		argspec = getfullargspec(handler)
		arglist = list(argspec.args)
		
		if ismethod(handler):
			del arglist[0]
		
		for i, value in enumerate(list(args)):
			key = arglist[i]
			if key in annotations:
				args[i] = cast(key, value)
		
		# Convert keyword arguments
		for key, value in list(items(kw)):
			if key in annotations:
				kw[key] = cast(key, value)
	
	def transform(self, context, handler, result):
		"""Transform the value returned by the controller endpoint.
		
		This extension transforms returned values if the endpoint has a return type annotation.
		"""
		handler = handler.__func__ if hasattr(handler, '__func__') else handler
		annotation = getattr(handler, '__annotations__', {}).get('return', None)
		
		if annotation:
			return (annotation, result)
		
		return result
