"""Web-based REPL shell and interactive debugger extension."""

from webob.exc import HTTPNotFound
from backlash import DebuggedApplication

from ..core.typing import Context, Optional, Tags, Request, WSGI


log = __import__('logging').getLogger(__name__)


class Console:
	"""Attach a console to your web application at an arbitrary location."""
	
	__slots__ = ('debugger', 'request')
	
	debugger: Optional[DebuggedApplication]
	request: Request
	
	def __init__(self, context:Context) -> None:
		# assert check_argument_types()
		
		self.request = context.request
		self.debugger = context.get('debugger', None)
	
	def __call__(self, *args, **kw):
		if not self.debugger: raise HTTPNotFound("Debugger extension unavailable.")
		return self.debugger.display_console(self.request)


class DebugExtension:
	"""Enable an interactive exception debugger and interactive console.
	
	Possible configuration includes:
	
		* `path` -- the path to the interactive console, defaults to: `/__console__`
		* `verbose` -- show ordinarily hidden stack frames, defaults to: `False`
	"""
	
	__slots__ = ('path', 'verbose')
	provides: Tags = {'debugger', 'console'}
	uses: Tags = {'waf'}
	
	path: str
	verbose: bool
	
	def __init__(self, path:str='/__console__', verbose:bool=False) -> None:
		# assert check_argument_types()
		if __debug__: log.debug("Initializing debugger extension.")
		
		self.path = path
		self.verbose = verbose
		
		super().__init__()
	
	def __call__(self, context:Context, app:WSGI) -> WSGI:
		"""Executed to wrap the application in middleware.
		
		The first argument is the application context, not request context.
		
		Accepts a WSGI application as the second argument and must likewise return a WSGI app.
		"""
		
		log.warning("Wrapping application in debugger middleware.")
		
		def _populate(locals:dict, context:Context) -> dict:
			"""Collect contributions from extensions to debugger/shell locals."""
			
			for ext in context.extension.signal.interactive:
				locals.extend(ext(context) or {})
			
			return locals
		
		#def init_console() -> dict:
		#	"""Add variables to the console context. REPL consoles operate at the application context scope."""
		#	return _populate({'context': context}, context)
		
		#def init_debugger(self, environ):
		#	"""Add variables to the debugger context. Debugger consoles operate at the request context scope."""
		#	return _populate({'context': environ.get('context')}, locals['context'])
		
		app = DebuggedApplication(
				app,
				evalex = __debug__,  # In production mode, this is a security no-no.
				show_hidden_frames = self.verbose,
				console_init_func = lambda: _populate({'context': context}, context),
				context_injectors = [lambda env: _populate({'context': context}, context)],
			)
		
		context.debugger = app
		
		return app
