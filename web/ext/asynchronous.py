"""Asynchronous support machinery and extension for WebCore.

As WebCore is not yet asynchronous internally, some effort needs to be expended to correctly interoperate. Primarily,
an event loop needs to be executing in order to process asynchronous invocations and awaiting behaviour. WebCore
accomplishes this by-if no existing loop is running-spawning one in a dedicated thread.

Do not mix this asynchronous extension with one providing futures thread- or process-based parallelism, as the order
the extensions are defined would determine which succeeds in providing the `submit` context method. Both futures and
async extensions provide this method in order to submit background tasks for execution. To be explicit, utilize
`context.loop` for asynchronous interactions, and `context.executor` for futures-based interactions.

To utilize, invoke an asynchronous function to acquire a coroutine handle and pass that handle to `context.submit`,
scheduling execution within the main thread with active event loop, or a dedicated thread for the asynchronous reactor
event loop. E.g.:

	async def hello(name): return f"Hello {name}!"
	
	future = context.submit(hello("world"))
	future.add_done_callback(...)  # Execute a callback upon completion of the asynchronous task.
	future.result()  # Will block the worker thread on the result of asynchronous execution within the event loop.
"""

import sys

from asyncio import AbstractEventLoop, get_event_loop, new_event_loop, set_event_loop, run_coroutine_threadsafe
from functools import partial
from threading import Thread
from typing import Optional

from web.core.context import Context


log = __import__('logging').getLogger('rita.util.async') # __name__)


class AsynchronousSupport:
	"""Support for asynchronous language functionality.
	
	Accepts a single configuration argument, `loop`, allowing you to explicitly define an event loop to utilize rather
	than relying upon default `new_event_loop` behaviour.
	"""
	
	loop: AbstractEventLoop  # The asynchronous event loop to utilize.
	thread: Optional[Thread] = None  # Offload asynchronous execution to this thread, if needed.
	
	def __init__(self, loop:Optional[AbstractEventLoop]=None):
		"""Prepare an asynchronous reactor / event loop for use, which may optionally be explicitly specified."""
		
		if not loop: loop = get_event_loop()
		if not loop: loop = new_event_loop()
		self.loop = loop
		
		if not loop.is_running():  # Thread of execution for asynchronous code if required.
			self.thread = Thread(target=self.thread, args=(loop, ), daemon=True, name='async')
	
	def start(self, context:Context):
		"""Executed on application startup."""
		
		if not self.loop.is_running():  # With no outer async executor, spawn our own in a dedicated thread.
			self.thread.start()
		
		# Expose our event loop at the application scope.
		context.loop = self.loop
		set_event_loop(self.loop)
		
		log.debug(f"Asynchronous event loop / reactor: {self.loop!r}")
		
		context.submit = partial(run_coroutine_threadsafe, loop=self.loop)
	
	def prepare(self, context:Context):
		"""Explicitly define the running asynchronous loop within our request worker thread."""
		
		set_event_loop(self.loop)
		
		# Global bind may be sufficient.
		# context.submit = partial(run_coroutine_threadsafe, loop=self.loop)
	
	def stop(self, context:Context):
		"""On application shutdown, tell the executor to stop itself.
		
		The worker thread, if utilized, is marked 'daemon' and stops with application process or when the reactor is
		shut down.
		"""
		
		self.loop.call_soon_threadsafe(self.loop.stop)
	
	def thread(self, loop:AbstractEventLoop):
		log.warn("Asynchronous event loop / reactor thread spawned.")
		set_event_loop(loop)
		loop.run_forever()
		log.warn("Asynchronous event loop / reactor shut down.")

