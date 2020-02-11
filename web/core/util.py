"""WebCore common utilities."""

# ## Imports

import logging

from threading import RLock
from typing import Optional

from marrow.package.canonical import name


# ## Module Global Constants

sentinel = object()  # A singleton value to allow `None` as a legal value.


# ## Utility Functions

def safe_name(thing) -> str:
	"""Attempt to resolve the canonical name for an object, falling back on the `repr()` if unable to do so."""
	try:
		return name(thing)
	except:
		return repr(thing)


# ## Context-Related Utility Classes

class lazy:
	"""Lazily record the result of evaluating a function and cache the result.
	
	This is a non-data descriptor which tells Python to allow the instance __dict__ to override. Intended to be used
	by extensions to add zero-overhead (if un-accessed) values to the context.
	"""
	
	def __init__(self, func, name:Optional[str]=None, doc:Optional[str]=None):
		self.__name__ = name or func.__name__
		self.__module__ = func.__module__
		self.__doc__ = func.__doc__
		self.lock = RLock()
		self.func = func
	
	def __get__(self, instance, type=None):
		if instance is None:  # Allow direct access to the non-data descriptor via the class.
			return self
		
		with self.lock:  # Try to avoid situations with parallel thread access hammering the function.
			value = instance.__dict__.get(self.__name__, sentinel)
			
			if value is sentinel:
				value = instance.__dict__[self.__name__] = self.func(instance)
		
		return value


def addLoggingLevel(levelName:str, levelNum:int, methodName:str=None) -> None:
	"""Comprehensively add a new logging level to the `logging` module and the current logging class.
	
	`levelName` becomes an attribute of the `logging` module with the value `levelNum`. `methodName` becomes a
	convenience method for both `logging` itself and the class returned by `logging.getLoggerClass()` (usually just
	`logging.Logger`). If `methodName` is not specified, `levelName.lower()` is used.
	
	To avoid accidental clobberings of existing attributes, this method will raise an `AttributeError` if the level
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
		raise AttributeError('{} already defined in logging module'.format(levelName))
	if hasattr(logging, methodName):
		raise AttributeError('{} already defined in logging module'.format(methodName))
	if hasattr(logging.getLoggerClass(), methodName):
		raise AttributeError('{} already defined in logger class'.format(methodName))
	
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
