# encoding: utf-8

"""Web-based REPL shell and interactive debugger extension."""

# ## Imports

from __future__ import unicode_literals

from webob.exc import HTTPNotFound
from backlash import DebuggedApplication


# ## Module Globals

log = __import__('logging').getLogger(__name__)


# ## Controller Endpoint Utility

class Console(object):
	"""Attach a console to your web application at an arbitrary location."""
	
	__slots__ = ('debugger', 'request')
	
	def __init__(self, context):
		self.debugger = context.get('debugger', None)
		self.request = context.request
	
	def __call__(self, *args, **kw):
		if not self.debugger:
			raise HTTPNotFound()
		
		return self.debugger.display_console(self.request)


# ## Extension

class DebugExtension(object):
	"""Enable an interactive exception debugger and interactive console.
	
	Possible configuration includes:
	
		* `path` -- the path to the interactive console, defaults to: `/__console__`
		* `verbose` -- show ordinarily hidden stack frames, defaults to: `False`
	"""
	
	__slots__ = ('path', 'verbose')
	
	provides = ['debugger', 'console']
	
	def __init__(self, path="/__console__", verbose=False):
		if __debug__:
			log.debug("Initializing debugger extension.")
		
		self.path = path
		self.verbose = verbose
		
		super(DebugExtension, self).__init__()
	
	def init_console(self):
		"""Add variables to the console context."""
		return dict()
	
	def init_debugger(self, environ):
		"""Add variables to the debugger context."""
		return dict(context=environ.get('context'))
	
	def __call__(self, context, app):
		"""Executed to wrap the application in middleware.
		
		The first argument is the application context, not request context.
		
		Accepts a WSGI application as the second argument and must likewise return a WSGI app.
		"""
		
		if __debug__:
			log.debug("Wrapping application in debugger middleware.")
		
		app = DebuggedApplication(
				app,
				evalex = __debug__,  # In production mode, this is a security no-no.
				show_hidden_frames = self.verbose,
				console_init_func = self.init_console,
				context_injectors = [self.init_debugger],
			)
		
		context.debugger = app
		
		return app
