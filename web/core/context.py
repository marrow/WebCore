# encoding: utf-8

from __future__ import unicode_literals

from collections import MutableMapping


class Context(MutableMapping):
	"""An attribute access dictionary, of a kind.
	
	This utility class is used to cooperatively construct the ApplicationContext (and subsequent RequestContext)
	from the contributions of multiple extensions. The concept of "promotion to a class" is needed in order to enable
	the use of descriptor protocol attributes; without promotion the protocol would not be utilized.
	"""
	
	# M-Morty! We're, *belch*, gonna have to go in deep, Morty!  Elbow deep!
	def _promote(self, name, instantiate=True):
		"""Create a new subclass of Context which incorporates instance attributes and new descriptors.
		
		This promotes an instance and its instance attributes up to being a class with class attributes, then
		returns an instance of that class.
		"""
		
		metaclass = type(self.__class__)
		contents = self.__dict__.copy()
		cls = metaclass(str(name), (self.__class__, ), contents)
		
		if instantiate:
			return cls()
		
		return cls
	
	def __init__(self, **kw):
		self.__dict__.update(kw)
		super(Context, self).__init__()
	
	def __len__(self):
		return len([i for i in (set(dir(self)) - self._STANDARD_ATTRS) if i[0] != '_'])
	
	def __iter__(self):
		"""Iterate all valid attributes/keys."""
		return (i for i in (set(dir(self)) - self._STANDARD_ATTRS) if i[0] != '_')
	
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

Context._STANDARD_ATTRS = set(dir(Context()))

