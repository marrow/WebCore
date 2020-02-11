"""Record basic performance statistics.

Record performance statistics about every aspect of the processing of each request, and report varying levels of
detail back to the requesting client or the application logs.

By default this extension:

* Adds a `Generation-Time` (in floating point seconds) header to all responses and logs this "generation time" at
  the `debug` level. This represents the time from the start of the request (as captured by a wrapping middleware
  layer, prior to WebCore application involvement) until the point the response is "returned" to the client (final
  "after" callback).

* Adds a complex `Server-Timing` header to the response, at a given level of detail:

  * `None` — do not deliver timing information.

  * `'basic'` — deliver only the global `total` and `app` times, the default.

  * `'all'` — deliver `total` and `app` times, as well as the durations of all extension callback phases.

You can disable these by passing `header=None` or `level=None` or `timing=None`, or specify an alternate logging
level by passing in the name of the level. This is the overall time from the start of request preparation until the
response has been populated, prior to being sent to the client.

The message logged will include the time spent in-application, the time spent in-framework (and extensions), and the
time taken to stream the response to the client.

If `timing` is enabled (which it is by default), Server-Timing headers will additionally be added. Ref:

* https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Server-Timing
* https://w3c.github.io/server-timing/

Callbacks are executed in this order:

	pre {prepare, before} →			# environment is prepared
		dispatch →					# endpoint discovery (multiple calls)
			collect →				# arguments to endpoint are collected
				! endpoint →		# endpoint is actually called
					transform →		# transform response prior to view invocation
						-after →		# returning response
							-done	# response delivered
"""

from time import time


log = __import__('logging').getLogger(__name__)



class AnalyticsExtension(object):
	"""Record performance statistics about each request, and potentially a lot more.
	
	By default this extension adds a `X-Generation-Time` header to all responses and logs the generation time at the
	`debug` level.  You can disable either by passing `header=None` or `level=None`, or specify an alternate logging
	level by passing in the name of the level.
	"""
	
	__slots__ = ('header', 'log')
	
	first = True  # We need this processing to happen as early as possible.
	provides = ['analytics']  # Expose this symbol for other extensions to depend upon.
	
	def __init__(self, header='X-Generation-Time', level='debug'):
		"""Executed to configure the extension."""
		
		super().__init__()
		
		self.header = header
		self.log = getattr(log, level) if level else None
	
	# ### Request-Local Callbacks
	
	def prepare(self, context):
		"""Executed during request set-up."""
		
		context._start_time = None
	
	def before(self, context):
		"""Executed after all extension prepare methods have been called, prior to dispatch."""
		
		context._start_time = time.time()
	
	def after(self, context, exc=None):
		"""Executed after dispatch has returned and the response populated, prior to anything being sent to the client."""
		
		duration = context._duration = round((time.time() - context._start_time) * 1000)  # Convert to ms.
		delta = unicode(duration)
		
		# Default response augmentation.
		if self.header:
			context.response.headers[self.header] = delta
		
		if self.log:
			self.log("Response generated in " + delta + " seconds.", extra=dict(
					duration = duration,
					request = id(context)
				))

