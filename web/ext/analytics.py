# encoding: utf-8

"""Record basic performance statistics."""

# ## Imports

from __future__ import unicode_literals

import time

from web.core.compat import unicode


# ## Module Globals

log = __import__('logging').getLogger(__name__)


# ## Extension

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
		
		super(AnalyticsExtension, self).__init__()
		
		# Record settings.
		self.header = header
		self.log = getattr(log, level) if level else None
	
	# ### Request-Local Callabacks
	
	def prepare(self, context):
		"""Executed during request set-up."""
		
		context._start_time = None
	
	def before(self, context):
		"""Executed after all extension prepare methods have been called, prior to dispatch."""
		
		context._start_time = time.time()
	
	def after(self, context, exc=None):
		"""Executed after dispatch has returned and the response populated, prior to anything being sent to the client."""
		
		duration = time.time() - context._start_time
		delta = unicode(round(duration, 5))
		
		# Default response augmentation.
		if self.header:
			context.response.headers[self.header] = delta
		
		if self.log:
			self.log("Response generated in " + delta + " seconds.", extra=dict(
					duration = duration,
					request = id(context)
				))

