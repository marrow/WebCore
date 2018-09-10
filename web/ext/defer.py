# encoding: utf-8

from __future__ import unicode_literals, print_function

import multiprocessing
import weakref

try:
	from concurrent import futures
except ImportError:
	print("To use the task deferral extension on your Python version, you must first install the 'futures' package.")
	raise

from web.core.util import lazy


log = __import__('logging').getLogger(__name__)


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
		if self._internal is None and self._schedule() is None:
			raise futures.CancelledError
		
		return self._internal.result(timeout)
	
	def exception(self, timeout=None):
		if self._internal is None and self._schedule() is None:
			raise futures.CancelledError
		
		return self._internal.exception(timeout)
	
	def add_done_callback(self, func):
		self.done_callbacks.append(func)
	
	def set_running_or_notify_cancel(self):
		if self._cancelled or self._internal:
			return False
		
		return True
	
	def _schedule(self, executor=None):
		if executor is None:
			if self._deferred:
				return self._deferred._schedule_one(self)
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
	
	def map(self, func, *iterables, **kw):
		timeout = kw.pop('timeout', None)
		chunksize = kw.pop('chunksize', 1)
		
		if kw:
			raise TypeError("map() got an unexpected keyword argument(s) '{}'".format("', '".join(kw)))
	
	def _schedule_one(self, future):
		return future._schedule(self._executor)
	
	def shutdown(self, wait=True):
		for future in self._futures:
			future._schedule(self._executor)
		
		self._futures = []


class DeferralExtension(object):
	"""Provide a Futures-compatible backround task executor that defers until after the headers have been sent.
	
	This exposes two executors: `executor` (generally a thread or process pool) and `defer`, a task pool that submits
	the tasks to the real executor only after the headers have been sent to the client. In this way, background tasks
	should have no visible impact on response generation times.
	"""
	
	provides = ['executor', 'deferral']
	
	def __init__(self, Executor=None, **config):
		"""Configure the deferral extension."""
		
		if Executor is None:
			if 'max_workers' not in config:
				config['max_workers'] = multiprocessing.cpu_count()
			
			Executor = futures.ThreadPoolExecutor
		
		self._config = config
		self._Executor = Executor
	
	def _get_deferred_executor(self, context):
		"""Lazily construct a deferred future executor."""
		return DeferredExecutor(context.executor)
	
	def _get_concrete_executor(self, context):
		"""Lazily construct an actual future executor implementation."""
		
		return self._Executor(**self._config)
	
	def start(self, context):
		"""Prepare the context with application-scope attributes on startup.
		
		The real Futures executor is constructed once, then re-used between requests.
		"""
		
		context.executor = self._Executor(**self._config)
	
	def prepare(self, context):
		"""Construct a context-local pool of deferred tasks, with request-local deferred executor."""
		
		context.defer = lazy(self._get_deferred_executor, 'defer')
	
	def done(self, context):
		"""After request processing has completed, submit any deferred tasks to the real executor."""
		
		if 'defer' not in context.__dict__:
			if __debug__:
				log.debug("Deferred tasks not accessed during this request; nothing to do.")
			
			return  # Bail early to prevent accidentally constructing the lazy value.
		
		# Within this context, deferral is done with.
		# Additionally, this will automatically schedule all submitted tasks with the real executor.
		context.defer.shutdown(wait=False)
	
	def stop(self, context):
		"""Drain the real executor on web service shutdown."""
		
		context.executor.shutdown(wait=True)
