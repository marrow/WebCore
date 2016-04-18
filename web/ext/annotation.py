# encoding: utf-8

"""Python 3 function annotation typecasting support."""

# ## Imports

from __future__ import unicode_literals

from inspect import ismethod, getfullargspec

from web.core.compat import items


# ## Extension

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
	"""
	
	__slots__ = tuple()
	
	provides = ['annotation', 'cast', 'typecast']  # Export these symbols for other extensions to depend upon.
	
	# ### Request-Local Callbacks
	
	def mutate(self, context, handler, args, kw):
		"""Inspect and potentially mutate the given handler's arguments.
		
		The args list and kw dictionary may be freely modified, though invalid arguments to the handler will fail.
		"""
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
				args[i] = annotations[key](value)
		
		# Convert keyword arguments
		for key, value in list(items(kw)):
			if key in annotations:
				kw[key] = annotations[key](value)
	
	def transform(self, context, handler, result):
		"""Transform the value returned by the controller endpoint.
		
		This extension transforms returned values if the endpoint has a return type annotation.
		"""
		handler = handler.__func__ if hasattr(handler, '__func__') else handler
		annotation = getattr(handler, '__annotations__', {}).get('return', None)
		
		if annotation:
			return (annotation, result)
		
		return result

