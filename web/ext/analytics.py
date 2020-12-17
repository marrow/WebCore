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

	pre {prepare, before}			# environment is prepared
		dispatch					# endpoint discovery (multiple calls)
			collect					# arguments to endpoint are collected
				! endpoint			# endpoint is actually called
					transform		# transform response prior to view invocation
						-after		# returning response
							-done	# response delivered
"""

from time import time
from warnings import warn

from ..core.typing import Any, Callable, Context, Tags, Optional, WSGI


log = __import__('logging').getLogger(__name__)


def _record(callback:str, *, debounce:bool=False) -> Callable:
	"""Factory to generate extension callback methods that record their invocation time as a milestone."""
	
	if debounce:
		def inner(self, context:Context, *args, **kw) -> None:
			if callback not in context.milestone:  # Only record the first occurrence of the event.
				context.milestone[callback] = time()
	
	else:  # An optimized version if we don't need to worry about the event happening more than once.
		def inner(self, context:Context, *args, **kw) -> None:
			context.milestone[callback] = time()
	
	inner.__name__ = callback.rstrip('-')
	
	return inner


class TimingPrefix:
	"""Record the "start time" of each extension callback phase."""
	
	first: bool = True  # This extension goes "first" in the execution stack for each extension callback.
	provides: Tags = {'timing.prefix'}  # Expose this symbol for other extensions to depend upon.
	
	def __init__(self, timing:str='all', header:str="Generation-Time", log:str='info'):
		self.timing = timing
		self.header = header
		self.log = getattr(__import__('logging').getLogger(__name__), log) if log else None
	
	def __call__(self, context:Context, app:WSGI) -> WSGI:
		"""Add the start time of request processing as early as possible, at the WSGI middleware stage."""
		
		def inner(environ, start_response):
			environ['_WebCore_request_start'] = time()
			return app(environ, start_response)
		
		return inner
	
	def prepare(self, context:Context) -> None:
		"""Initial population of the context timing milestone storage."""
		context.milestone = {'init': context.environ['_WebCore_request_start'], 'prepare': time()}
	
	dispatch = _record('dispatch', debounce=True)
	before = _record('before')
	collect = _record('collect')
	
	def transform(self, context:Context, endpoint:Callable, result:Any) -> Any:
		"""Capture of the transformation stage timing, returning the unmodified result."""
		context.milestone['transform-'] = time()
		return result
	
	def after(self, context:Context) -> None:
		"""Executed after the response has been populated, prior to anything being sent to the client.
		
		We augment the response with our performance analytic headers here.
		"""
		
		now = context.milestone['after-'] = time()
		resp = context.response
		m = context.milestone
		deltas = {
				'app': m['transform'] - m['collect-'],
				'view': m['after'] - m['transform-'],
				'total': now - m['init'],
			}
		
		if self.log: self.log(f"Response prepared in {deltas['view'] * 1000} milliseconds.", extra=deltas)
		if self.header: resp.headers[self.header] = str(deltas['total'])
		if not self.timing: return
		
		if self.timing == 'all':
			deltas.update({k: m[f'{k}-'] - v for k, v in m.items() if f'{k}-' in m})
		
		resp.headers['Server-Timing'] = ', '.join(f'{k};dur={round(v * 1000, 1)}' for k, v in deltas.items())
	
	def done(self, context:Context) -> None:
		context.milestone['done-'] = time()
		
		if not self.log: return
		
		m = context.milestone
		deltas = {
				'app': m['transform'] - m['collect-'],
				'view': m['after'] - m['transform-'],
				'send': m['done'] - m['after-'],
				'total': m['done-'] - m['init'],
			**{k: m[f'{k}-'] - v for k, v in m.items() if f'{k}-' in m}}
		
		self.log(f"Response delivered in {deltas['send'] * 1000} milliseconds.", extra=deltas)


class TimingExtension:
	"""Record the end time of each callback phase, then generate HTTP response headers and logging output."""
	
	__slots__ = ('header', 'log', 'timing')
	
	last: bool = True
	needs: Tags = {'timing.prefix'}  # We depend on the timing information generated by these.
	uses: Tags = {'args.validation', 'kwargs.validation'}
	provides: Tags = {'timing.suffix', 'analytics'}  # Expose these symbols for other extensions to depend upon.
	
	header: Optional[str]  # The HTTP header name to assign overall generation time to.
	log: Optional[Callable]  # The function to invoke to generate a log entry.
	timing: Optional[str]  # Server-Timing header level of detail. One of: None, 'basic', or 'all'.
	
	def __init__(self, header:Optional[str]='Generation-Time', level:Optional[str]='debug', timing:Optional[str]='basic'):
		"""Executed to configure the extension."""
		
		super().__init__()
		
		if timing not in (None, 'basic', 'all'):
			raise TypeError("Argument 'timing' must be one of: None, 'basic', or 'all'.")
		
		self.header = header
		self.log = getattr(log, level) if level else None
		self.timing = timing
	
	prepare = _record('prepare-')
	dispatch = _record('dispatch-')  # Not debounced here, because we want the _last_ dispatch event.
	before = _record('before-')
	collect = _record('collect-')
	
	def transform(self, context:Context, endpoint:Callable, result:Any) -> Any:
		"""Capture of the transformation stage timing, returning the unmodified result."""
		
		now = context.milestone['transform'] = time()
		delta = now - context.milestone['collect-']
		if self.log: self.log(f"Endpoint executed in {delta} seconds.")
		
		return result
	
	after = _record('after')
	done = _record('done')


class AnalyticsExtension(TimingExtension):
	"""A legacy adapter to modernize old API usage and provide a warning that such use is deprecated."""
	
	def __init__(self, header:Optional[str]='X-Generation-Time', level:Optional[str]='debug'):
		warn("Use of `AnalyticsExtension` is deprecated. Use the more capable and standards-based `TimingExtension`.",
				DeprecationWarning, stacklevel=2)
		
		super().__init__(header, level, None)
