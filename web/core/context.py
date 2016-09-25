# encoding: utf-8

"""A `MutableMapping` subclass for use as a request-local context object."""

# ## Imports

from __future__ import unicode_literals

from collections import MutableMapping


# ## Mapping Class

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
		"""Construct a new Context instance.
		
		All keyword arguments are applied to the instance as attributes through direct assignment to `__dict__`.
		"""
		self.__dict__.update(kw)
		super(Context, self).__init__()
	
	def __len__(self):
		"""Get a list of the public data attributes."""
		return len([i for i in (set(dir(self)) - self._STANDARD_ATTRS) if i[0] != '_'])
	
	def __iter__(self):
		"""Iterate all valid (public) attributes/keys."""
		return (i for i in (set(dir(self)) - self._STANDARD_ATTRS) if i[0] != '_')
	
	def __getitem__(self, name):
		"""Retrieve an attribute through dictionary access."""
		try:
			return getattr(self, name)
		except AttributeError:
			pass
		
		# We do this here to avoid Python 3's nested exception support.
		raise KeyError(name)
	
	def __setitem__(self, name, value):
		"""Assign an attribute through dictionary access."""
		setattr(self, name, value)
	
	def __delitem__(self, name):
		"""Delete an attribute through dictionary access."""
		try:
			return delattr(self, name)
		except AttributeError:
			pass
		
		# We do this here to avoid Python 3's nested exception support.
		raise KeyError(name)

# We generally want to exclude "default object attributes" from the context's list of attributes.
# This auto-detects the basic set of them for exclusion from iteration in the above methods.
Context._STANDARD_ATTRS = set(dir(Context()))



class ContextGroup(Context):
	"""A managed group of related context additions.
	
	This proxies most attribute access through to the "default" group member.
	
	Because of the possibility of conflicts, all attributes are accessible through dict-like subscripting.
	
	Register new group members through dict-like subscript assignment as attribute assignment is passed through to the
	default handler if assigned.
	"""
	
	default = None
	
	def __init__(self, default=None, **kw):
		if default is not None:
			self.default = default
			default.__name__ = 'default'
		
		for name in kw:
			kw[name].__name__ = name
			self.__dict__[name] = kw[name]
	
	def __repr__(self): 
		return "{0.__class__.__name__}({1})".format(self, ', '.join(sorted(self)))
	
	def __len__(self):
		return len(self.__dict__)
	
	def __iter__(self):
		return iter(set(dir(self)) - self._STANDARD_ATTRS)
	
	def __getitem__(self, name):
		try:
			return getattr(self, name)
		except AttributeError:
			pass
		
		raise KeyError()
	
	def __setitem__(self, name, value):
		self.__dict__[name] = value
	
	def __delitem__(self, name):
		del self.__dict__[name]
	
	def __getattr__(self, name):
		if self.default is None:
			raise AttributeError()
		
		return getattr(self.default, name)
	
	def __setattr__(self, name, value):
		if self.default is not None:
			return setattr(self.default, name, value)
		
		self.__dict__[name] = value
	
	def __delattr__(self, name):
		if self.default is not None:
			return delattr(self.default, name)
		
		self.__dict__[name] = None
		del self.__dict__[name]

ContextGroup._STANDARD_ATTRS = set(dir(ContextGroup()))

