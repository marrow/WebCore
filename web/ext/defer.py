# encoding: utf-8

# Imports

from __future__ import unicode_literals

import weakref

try:
	from concurrent import futures
except ImportError:
	print("You must install the 'futures' package.")
	raise

from web.core.util import lazy

# Module Globals

log = __import__('logging').getLogger(__name__)

# Extension


class DeferredFuture(object):
	__slots__ = ['_deferred', '_func', '_cancelled', '_internal', '_done_callbacks']
	
	def __init__(self, deferred, func, *args, **kwargs):
		self._deferred = deferred
		self._func = (func, args, kwargs)
		self._cancelled = False
		self._internal = None
		self._done_callbacks = []
	
	def cancel(self):
		if self._internal is not None:
			return False
		
		self._cancelled = True
		return True
	
	def cancelled(self):
		return self._cancelled or (self._internal and self._internal.cancelled())
	
	def running(self):
		return self._internal is not None and self._internal.running()
	
	def done(self):
		return self._internal and self._internal.done()
	
	def result(self, timeout=None):
		if self._internal is None and self.schedule() is None:
			raise futures.CancelledError
		
		return self._internal.result(timeout)
	
	def exception(self, timeout=None):
		if self._internal is None and self.schedule() is None:
			raise futures.CancelledError
		
		return self._internal.exception(timeout)
	
	def add_done_callback(self, func):
		self.done_callbacks.append(func)
	
	def set_running_or_notify_cancel(self):
		if self._cancelled or self._internal:
			return False
		
		return True
	
	def schedule(self, executor=None):
		if executor is None:
			if self._deferred:
				return self._deferred.schedule_one(self)
			raise Exception # Shouldn't be accessible this early in the process lifecycle...
		
		if self.set_running_or_notify_cancel() is False:
			return None
		
		self._internal = executor.submit(self._func[0], *self._func[1], **self._func[2])
		assert self._internal is not None
		
		for cb in self._done_callbacks:
			self._internal.add_done_callback(cb)
		return self._internal


class DeferredExecutor(object):
	__slots__ = ['_futures', '_executor', '__weakref__']
	
	def __init__(self, executor):
		self._futures = []
		self._executor = executor
	
	def submit(self, func, *args, **kwargs):
		future = DeferredFuture(weakref.proxy(self), func, *args, **kwargs)
		self._futures.append(future)
		return future
	
	def map(self, func, *iterables, timeout=None, chunksize=1):
		pass
	
	def schedule_one(self, future):
		return future.schedule(self._executor)
	
	def shutdown(self, wait=True):
		if wait is False:
			self._futures = []
			return
		
		while len(self._futures) > 0:
			self._futures.pop(0).schedule(self._executor)


class DeferralExtension(object):
	"""Provide an interface on RequestContext to defer a background function call until after the response has finished
	streaming to the browser.
	
	A mock executor interface will be added at `context.deferred_executor` that will preserve calls until the
	extension's 'done' callback at which point the extension will flush commands to a configurable internal executor.
	"""
	
	provides = ['executor', 'deferral']
	
	def __init__(self, Executor=None, **config):
		"""Configure the deferral extension.
		"""
		
		if Executor is None:
			if 'max_workers' not in config:
				config['max_workers'] = 5

			Executor = futures.ThreadPoolExecutor
		
		self._config = config
		self._Executor = Executor
	
	def _get_deferred_executor(self, context):
		return DeferredExecutor(weakref.proxy(context.executor))
	
	def start(self, context):
		context.executor = self._Executor(**self._config)
		context.deferred_executor = lazy(self._get_deferred_executor, 'deferred_executor')
	
	def stop(self, context):
		context.executor.shutdown(wait=True)
	
	def done(self, context):
		if 'deferred_executor' not in context.__dict__: # Check if there's even any work to be done
			log.debug("Deferred executor not accessed during request")
			return
		
		context.deferred_executor.shutdown(wait=True)
		log.debug("Deferred executor accessed")
