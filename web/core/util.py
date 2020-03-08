"""WebCore common utilities."""

import logging

from threading import RLock
from typing import Any, Callable, Optional, Type
from pathlib import PurePosixPath

from marrow.package.canonical import name


# Constants & Data Structures

sentinel = object()  # A singleton value to allow `None` as a legal value.

Crumb = namedtuple('Breadcrumb', ('handler', 'path'))


# Utility Functions

def safe_name(thing) -> str:
	"""Attempt to resolve the canonical name for an object, falling back on the `repr()` if unable to do so."""
	try:
		return name(thing)
	except:
		return repr(thing)


def nop(body:str) -> Iterable:
	"""A de-serializer no-operation to prevent contribution by this type, as it is handled separately."""
	return ()  # More efficient to extend by an empty tuple than to involve mapping processing.


def addLoggingLevel(levelName:str, levelNum:int, methodName:str=None) -> None:
	"""Comprehensively add a new logging level to the `logging` module and the current logging class.
	
	`levelName` becomes an attribute of the `logging` module with the value `levelNum`. `methodName` becomes a
	convenience method for both `logging` itself and the class returned by `logging.getLoggerClass()` (usually just
	`logging.Logger`). If `methodName` is not specified, `levelName.lower()` is used.
	
	To avoid accidental clobbering of existing attributes, this method will raise an `AttributeError` if the level
	name is already an attribute of the `logging` module or if the method name is already present.
	
	From: https://stackoverflow.com/a/35804945/211827
	
	Example
	-------
	>>> addLoggingLevel('TRACE', logging.DEBUG - 5)
	>>> logging.getLogger(__name__).setLevel("TRACE")
	>>> logging.getLogger(__name__).trace('that worked')
	>>> logging.trace('so did this')
	>>> logging.TRACE
	5
	"""
	
	if not methodName:
		methodName = levelName.lower()
	
	if hasattr(logging, levelName):
		raise AttributeError(f'{levelName} already defined in logging module')
	if hasattr(logging, methodName):
		raise AttributeError(f'{methodName} already defined in logging module')
	if hasattr(logging.getLoggerClass(), methodName):
		raise AttributeError(f'{methodName} already defined in logger class')
	
	# This method was inspired by the answers to Stack Overflow post
	# http://stackoverflow.com/q/2183233/2988730, especially
	# http://stackoverflow.com/a/13638084/2988730
	def logForLevel(self, message, *args, **kwargs):
		if self.isEnabledFor(levelNum):
			self._log(levelNum, message, args, **kwargs)
	def logToRoot(message, *args, **kwargs):
		logging.log(levelNum, message, *args, **kwargs)
	
	logging.addLevelName(levelNum, levelName)
	setattr(logging, levelName, levelNum)
	setattr(logging.getLoggerClass(), methodName, logForLevel)
	setattr(logging, methodName, logToRoot)


# Context-Related Utility Classes

class lazy:
	"""Lazily record the result of evaluating a function and cache the result.
	
	This is a descriptor which tells Python to allow the instance __dict__ to override. Intended to be used by
	extensions to add zero-overhead (if not accessed) values to the request context. It replaces itself within the
	instance so subsequent access will be direct if given the appropriate name.
	"""
	
	__name__: str
	__module__: str
	__doc__: str
	lock: RLock
	func: Callable
	
	def __init__(self, func:Callable, name:Optional[str]=None, doc:Optional[str]=None) -> None:
		self.__name__ = name or func.__name__
		self.__module__ = func.__module__
		self.__doc__ = func.__doc__
		self.lock = RLock()
		self.func = func
		
		if 'return' in func.__annotations__:  # Copy over the annotation to accurately announce typing.
			self.__get__.__annotations__['return'] = func.__annotations__['return']
	
	def __get__(self, instance:Optional[Any], type:Optional[Type]=None) -> Any:
		"""Retrieve this descriptor, attempt to retrieve by name, or execute the associated callback and store."""
		
		if instance is None:  # Allow direct access to the non-data descriptor via the class.
			return self
		
		with self.lock:  # Try to avoid situations with parallel thread access hammering the function.
			value = instance.__dict__.get(self.__name__, sentinel)  # Retrieve the value directly from the instance.
			
			if value is sentinel:  # If the named attribute is not present, calculate it and store.
				value = instance.__dict__[self.__name__] = self.func(instance)
		
		return value


class Bread(list):
	"""A trivial derivative list that provides an accessor property to access the final element's path attribute."""
	
	@property
	def current(self) -> PurePosixPath:
		return self[-1].path
