# encoding: utf-8

"""Interactive tracebacks for WebCore."""



class DebuggingExtension(object):
	provides = ['debug']
	last = True
	
	def __init__(self):
		"""Executed to configure the extension."""
		
		super(DebuggingExtension, self).__init__()
	
	def __call__(self, context, app):
		"""Executed to wrap the application in middleware."""
		pass
