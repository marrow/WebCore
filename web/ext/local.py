# encoding: utf-8

# ## Imports

from __future__ import unicode_literals

from threading import local

from marrow.package.loader import traverse


# ## Module Globals

# Standard logger object.
log = __import__('logging').getLogger(__name__)


# ## Extension

class ThreadLocalExtension(object):
	"""Provide the current context as a thread local global.
	
	This provides a convienent "superglobal" variable where you can store per-thread data.
	
	While the context itself is cleaned up after each call, any data you add won't be.  These are not request-locals.
	"""
	
	first = True
	provides = ['local', 'threadlocal']
	
	def __init__(self, where='web.core:local'):
		"""Initialize thread local storage for the context.
		
		By default the `local` object in the `web.core` package will be populated as a `threading.local` pool. The
		context, during a request, can then be accessed as `web.core.local.context`. Your own extensions can add
		additional arbitrary data to this pool.
		"""
		
		super(ThreadLocalExtension, self).__init__()
		
		if __debug__:
			log.debug("Initalizing ThreadLocal extension.")
		
		self.where = where
		self.local = None
		self.preserve = False
	
	def _lookup(self):
		module, _, name = self.where.rpartition(':')
		module = traverse(__import__(module), '.'.join(module.split('.')[1:]), separator='.')
		
		return module, name
	
	def start(self, context):
		module, name = self._lookup()
		
		if __debug__:
			log.debug("Preparing thread local storage and assigning main thread application context.")
		
		if hasattr(module, name):
			self.local = getattr(module, name)
			self.preserve = True
		else:
			self.local = local()
			setattr(module, name, self.local)
		
		self.local.context = context  # Main thread application context.
	
	def stop(self, context):
		self.local = None
		
		if __debug__:
			log.debug("Cleaning up thread local storage.")
		
		if not self.preserve:
			module, name = self._lookup()
			delattr(module, name)
	
	def prepare(self, context):
		"""Executed prior to processing a request."""
		if __debug__:
			log.debug("Assigning thread local request context.")
		
		self.local.context = context
	
	def done(self, result):
		"""Executed after the entire response has been sent to the client."""
		if __debug__:
			log.debug("Cleaning up thread local request context.")
		
		del self.local.context

