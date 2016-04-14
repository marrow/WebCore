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
	"""Typecast the arguments to your controllers using Python 3 function annotations."""
	
	__slots__ = ('handler', )
	
	provides = ['annotation', 'cast', 'typecast']
	
	def __init__(self, encoding='utf-8', fallback='iso-8859-1'):
		super(CastExtension, self).__init__()
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

