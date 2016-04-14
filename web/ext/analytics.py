# encoding: utf-8

from __future__ import unicode_literals

import time

from web.core.compat import unicode


class AnalyticsExtension(object):
	"""Record performance statistics about each request, and potentially a lot more.
	
	By default this extension adds a `X-Generation-Time` header to all responses and logs the generation time at the
	`debug` level.  You can disable either by passing `header=None` or `log=None`, or specify an alternate logging
	level by passing in the name of the level.
	
	In the future you'll be able to define a MongoDB database connection to log performance data, and the
	complete context including request and response.
	
	Finally, if you enable the inspector this extension will add a request generation time gadget to the central HUD.
	You can disable this inspector addition by passing in `panel=False`.  (This will only be used if the `inspect`
	extension itself is enabled.)
	"""
	
	__slots__ = ('header', 'log', 'panel')
	
	first = True
	uses = ['inspect']
	provides = ['analytics']
	
	def __init__(self, header='X-Generation-Time', log='debug', panel=True):
		"""Executed to configure the extension."""
		
		# TODO: db URI, collection='analytic', and expires=None (timedelta)
		
		super(AnalyticsExtension, self).__init__()
		
		# Record settings.
		self.header = header
		self.log = log
		self.panel = bool(panel)
	
	def start(self, context):
		"""Executed during application startup just after binding the server."""
		
		def dummy_logger(*args, **kw):
			pass
		
		# TODO: Prepare MongoDB connection.
		# Ensure the expiry index if expires is not None.
		
		pass
	
	def stop(self, context):
		"""Executed during application shutdown after the last request has been served."""
		
		# TODO: Drain the connection pool.
		
		pass
	
	def prepare(self, context):
		"""Executed during request set-up."""
		
		context._start_time = None
	
	def before(self, context):
		"""Executed after all extension prepare methods have been called, prior to dispatch."""
		context._start_time = time.time()
	
	def after(self, context, exc=None):
		"""Executed after dispatch has returned and the response populated, prior to anything being sent to the client."""
		
		delta = unicode(round(time.time() - context._start_time, 5))
		
		# Default response augmentation.
		if self.header:
			context.response.headers[self.header] = delta
		
		if self.log:
			getattr(context.log, self.log)("Response generated in " + delta + " seconds.")
		
		# TODO: Record context (and exception) to MongoDB.
	
	def inspect(self, context):
		"""Return an object conforming to the inspector panel API."""
		
		pass  # TODO: Not implemented yet, reference #141.

