# encoding: utf-8

from __future__ import unicode_literals

from inspect import ismethod
from functools import partial

try:
	from inspect import getfullargspec as getargspec
except ImportError:
	from inspect import getargspec

from web.core.compat import unicode


def unicodestr(s, encoding='utf-8', fallback='iso-8859-1'):
	"""Convert a string to unicode if it isn't already."""
	
	if isinstance(s, unicode):
		return s
	
	try:
		return s.decode(encoding)
	except UnicodeError:
		return s.decode(fallback)


class AnnotationExtension(object):
	"""Utilize Python 3 function annotations as a method to filter arguments coming in from the web.
	
	Argument annotations are treated as callbacks to execute, passing in the unicode value coming in from the web and
	swapping it with the value returned by the callback. This allows for trivial typecasting to most built-in Python
	types such as `int`, `float`, etc., as well as creative use such as `','.split` to automatically split a comma-
	separated value. One can of course also write custom callbacks, notably ones that raise `HTTPException`
	subclasses to not appear as an Internal Server Error.
	
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
	
	Explicitly requesting unicode casting will instead utilize a conversion function that can try a fallback encoding.
	By default the `encoding` option is `utf-8`, and the `fallback` is `iso-8859-1`.
	"""
	
	__slots__ = ('handler', )
	
	provides = ['annotation', 'cast', 'typecast']
	
	def __init__(self, encoding='utf-8', fallback='iso-8859-1'):
		"""Instantiate an AnnotationExtension."""
		
		super(AnnotationExtension, self).__init__()
		self.handler = partial(unicodestr, encoding=encoding, fallback=fallback)
	
	def mutate(self, context, handler, args, kw):
		"""Inspect and potentially mutate the given handler's arguments.
		
		The args list and kw dictionary may be freely modified, though invalid arguments to the handler will fail.
		"""
		annotations = getattr(handler.__func__ if hasattr(handler, '__func__') else handler, '__annotations__', None)
		if not annotations:
			return
		
		for k in annotations:
			if annotations[k] == unicode:
				annotations[k] = self.handler
		
		argspec = getargspec(handler)
		arglist = list(argspec.args)
		
		if ismethod(handler):
			del arglist[0]
		
		for i, value in enumerate(list(args)):
			key = arglist[i]
			if key in annotations:
				args[i] = annotations[key](value)
		
		# Convert keyword arguments
		for key, value in list(kw.items()):
			if key in annotations:
				kw[key] = annotations[key](value)
	
	def transform(self, context, handler, result):
		handler = handler.__func__ if hasattr(handler, '__func__') else handler
		annotation = getattr(handler, '__annotations__', {}).get('return', None)
		
		if annotation:
			return (annotation, result)
		
		return result

