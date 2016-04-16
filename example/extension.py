# encoding: utf-8


class Extension(object):
	"""A template of a WebCore 2 extension.
	
	Only the __init__ method is requried.
	
	The class attributes listed below control ordering and activation of other extensions.
	
	`uses`:
	:   Used for extension sorting and dependency graphing; if these features are present we can use them.
	`needs`:
	:   As per `uses`, but requires the named features be present.
	`always`:
	:   If `True` always load this extension.  Useful for application-provided extensions.
	`never`:
	:   The opposite of `always`.
	`first`:
	:   Always try to be first in the extension stack.
	`last`:
	:   Always try to be last in the extension stack.
	`provides`:
	:   A list of keywords usable in `uses` and `needs` declarations.
	`extensions`:
	:   A tuple of entry_point namespaces to search for extensions.
	
	The names of method arguments are unimportant; all values are passed positionally.
	"""
	
	uses = []
	needs = []
	always = False
	never = False
	first = False
	last = False
	provides = []
	extensions = ()
	
	def __init__(self, **config):
		"""Executed to configure the extension.
		
		No actions must be performed here, only configuration management.
		
		You can also update the class attributes here.  It only really makes sense to add dependencies.
		"""
		
		super(Extension, self).__init__()
	
	def __call__(self, context, app):
		"""Executed to wrap the application in middleware.
		
		The first argument is the global context class, not request-local context instance.
		
		Accepts a WSGI application as the second argument and must likewise return a WSGI app.
		"""
		
		return app
	
	def start(self, context):
		"""Executed during application startup just after binding the server.
		
		The first argument is the global context class, not request-local context instance.
		
		Any of the actions you wanted to perform during `__init__` you should do here.
		"""
		
		pass
	
	def stop(self, context):
		"""Executed during application shutdown after the last request has been served.
		
		The first argument is the global context class, not request-local context instance.
		"""
		pass
	
	def graceful(self, context, **config):
		"""Called when a SIGHUP is sent to the application.
		
		The first argument is the global context class, not request-local context instance.
		
		Allows your code to re-load configuration and your code should close then re-open sockets and files.
		"""
		pass
	
	def prepare(self, context):
		"""Executed during request set-up to populate the thread-local `context` instance.
		
		The purpose of the extension ordering is to ensure that methods like these are executed in the correct order.
		"""
		pass
	
	def dispatch(self, context, consumed, handler, is_endpoint):
		"""Executed as dispatch descends into a tier.
		
		The `consumed` argument is a Path object containing one or more path elements.
		The `handler` argument is the literal object that was selected to process the consumed elements.
		The `is_endpoint` argument is `True` if there will be no futher dispatch.
		
		Generally called in series, like:
		
			# Index method example.
			dispatch(context, '', RootController, True)
			
			# Data-based example.
			dispatch(context, '', RootController, False)
			dispatch(context, 'admin', AdminController, False)
			dispatch(context, 'user', UsersController, False)
			dispatch(context, '27', UserController(27), False)
			dispatch(context, 'modify', UserController(27).modify, True)
			
			# Contentment example.
			dispatch(context, '', AssetController, False)
			dispatch(context, 'company/about/staff', PageController, False)
			dispatch(context, 'view:page', PageController.page, True)
			
			# Route example.
			dispatch(context, '/admin/user/27/modify', modify_user, True)
		"""
		
		pass
	
	def before(self, context):
		"""Executed after all extension prepare methods have been called, prior to dispatch."""
		pass
	
	def after(self, context):
		"""Executed after dispatch has returned and the response populated, prior to anything being sent to the client.
		
		Similar to middleware, the first extension registered has its `after` method called last.
		"""
		pass
	
	def mutate(self, context, handler, args, kw):
		"""Inspect and potentially mutate the given handler's arguments.
		
		The args list and kw dictionary may be freely modified, though invalid arguments to the handler will fail.
		"""
		pass
	
	def transform(self, contexti, handler, result):
		"""Transform outgoing values prior to view lookup."""
		pass
	
	def interactive(self):
		"""Populate an interactive shell."""
		return dict()
	
	def inspect(self, context):
		"""Return an object conforming to the inspector panel API."""
		
		pass
