# encoding: utf-8

"""A port of the excellent Django Debug Toolbar to WebCore."""



class DebuggingExtension(object):
	provides = ['debug']
	last = True
	
	def __init__(self, context):
		"""Executed to configure the extension."""
		
		super(DebuggingExtension, self).__init__()
	
	def __call__(self, context, app):
		"""Executed to wrap the application in middleware."""
		pass
	
	def start(self, context):
		"""Executed during application startup just after binding the server."""
		pass
	
	def stop(self, context):
		"""Executed during application shutdown after the last request has been served."""
		pass
	
	def prepare(self, context):
		"""Executed during request set-up."""
		context._debug = object()
		
	
	def before(self, context):
		"""Executed after all extension prepare methods have been called, prior to dispatch."""
		pass
	
	def after(self, context, exc=None):
		"""Executed after dispatch has returned and the response populated, prior to anything being sent to the client."""
		pass
