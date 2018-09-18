# encoding: utf-8

from __future__ import unicode_literals, print_function

import multiprocessing
import weakref

try:
	from concurrent import futures
except ImportError:  # pragma: no cover
	print("To use the task deferral extension on your Python version, you must first install the 'futures' package.")
	raise

from web.core.util import lazy


log = __import__('logging').getLogger(__name__)


class DeferredFuture(object):
	"""A deferred (mock) future.
	
	Stores the task information needed to submit the callable and arguments to a real executor plus the done callbacks
	to be called upon completion of the real future.
	"""
	
	__slots__ = ['_ctx', '_func', '_cancelled', '_internal', '_callbacks']
	
	def __init__(self, _context, _func, *args, **kwargs):
		"""Construct a deferred, mock future."""
		self._ctx = _context
		self._func = (_func, args, kwargs)
		self._cancelled = False
		self._internal = None
		self._callbacks = []
	
	def cancel(self):
		if self._internal:
			return self._internal.cancel()  # TODO: Test this.
		
		self._cancelled = True
		return True
	
	def cancelled(self):
		return bool(self._cancelled or (self._internal and self._internal.cancelled()))
	
	def running(self):
		return bool(self._internal and self._internal.running())
	
	def done(self):
		return bool(self._internal and self._internal.done())
	
	def result(self, timeout=None):
		if not self._internal and not self._schedule():
			raise futures.CancelledError()  # TODO: Test this.
		
		return self._internal.result(timeout)
	
	def exception(self, timeout=None):
		if not self._internal and not self._schedule():
			raise futures.CancelledError()  # TODO: Test this.  I'm sensing a pattern, here.
		
		return self._internal.exception(timeout)
	
	def add_done_callback(self, func):
		self._callbacks.append(func)
	
	def set_running_or_notify_cancel(self):
		if self._cancelled or self._internal:
			return False
		
		return True  # dubious about this...
	
	def _schedule(self, executor=None):
		"""Schedule this deferred task using the provided executor.
		
		Will submit the task, locally note the real future instance (`_internal` attribute), and attach done
		callbacks.  Calling any of the standard Future methods (e.g. `result`, `done`, etc.) will first schedule the
		task, then execute the appropriate method by proxy.
		"""
		
		if not executor:
			executor = self._ctx.executor
		
		if not self.set_running_or_notify_cancel():
			return None
		
		self._internal = executor.submit(self._func[0], *self._func[1], **self._func[2])
		assert self._internal is not None
		
		for fn in self._callbacks:
			self._internal.add_done_callback(fn)
		
		return self._internal
	
	def __repr__(self):
		callbacks = len(self._callbacks)
		return '{0.__class__.__name__}({0._func[0]}, *{0._func[1]!r}, **{0._func[2]!r}, callbacks={1})'.format(self, callbacks)


class DeferredExecutor(object):
	__slots__ = ['_futures', '_ctx']
	
	def __init__(self, context):
		self._futures = []
		self._ctx = context
	
	def submit(self, func, *args, **kwargs):
		future = DeferredFuture(self._ctx, func, *args, **kwargs)
		self._futures.append(future)
		return future
	
	def map(self, func, *iterables, **kw):
		return self._ctx.executor.map(func, *iterables, **kw)
	
	def shutdown(self, wait=True):
		futures = [future._schedule() for future in self._futures]
		self._futures = []
		
		if wait:
			list(as_completed(futures, timeout=None if wait is True else wait))


class DeferralExtension(object):
	"""Provide a Futures-compatible backround task executor that defers until after the headers have been sent.
	
	This exposes two executors within the context: `executor` (generally a thread or process pool) and `defer`, a
	task pool that submits the tasks to the real executor only after the headers have been sent to the client. In this
	way, background tasks should have no visible impact on response generation times.
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
		return DeferredExecutor(context)
	
	def _get_concrete_executor(self, context):
		"""Lazily construct an actual future executor implementation."""
		
		return self._Executor(**self._config)
	
	def start(self, context):
		"""Prepare the context with application-scope attributes on startup.
		
		The real Futures executor is constructed once, then re-used between requests.
		"""
		
		context.executor = self._Executor(**self._config)
		context.defer = lazy(self._get_deferred_executor, 'defer')
	
	def prepare(self, context):
		"""Construct a context-local pool of deferred tasks, with request-local deferred executor."""
		
		pass
	
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
