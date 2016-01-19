# encoding: utf-8

from __future__ import unicode_literals

from collections import MutableMapping


class Context(MutableMapping):
	"""An attribute access dictionary, of a kind."""
	
	# M-Morty! We're, *belch*, gonna have to go in deep, Morty!  Elbow deep!
	def _promote(self, name="Context", instantiate=True):  # Having them all named Context may be confusing...
		"""Create a new subclass of Context which incorporates instance attributes and new descriptors.
		
		This promotes an instance and its instance attributes up to being a class with class attributes, then
		returns an instance of that class.
		"""
		
		metaclass = type(self.__class__)
		contents = self.__dict__.copy()
		cls = metaclass(name, (self.__class__, ), contents)
		
		if instantiate:
			return cls()
		
		return cls
	
	def __init__(self, **kw):
		self.__dict__.update(kw)
		super(Context, self).__init__()
	
	def __len__(self):
		return len(iter(self))
	
	def __iter__(self):
		"""Iterate all valid attributes/keys."""
		return (i for i in dir(self) if i[0] != '_')
	
	def __getitem__(self, name):
		try:
			return getattr(self, name)
		except AttributeError:
			pass
		
		# We do this here to avoid Python 3's nested exception support.
		raise KeyError(name)
	
	def __setitem__(self, name, value):
		setattr(self, name, value)
	
	def __delitem__(self, name):
		try:
			return delattr(self, name)
		except AttributeError:
			pass
		
		# We do this here to avoid Python 3's nested exception support.
		raise KeyError(name)
