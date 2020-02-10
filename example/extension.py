class Extension:
	"""A template for or example of a WebCore extension.
	
	Only the __init__ method is required.  For application-specific callback implementations, subclass
	web.core.Application and define these callbacks on your application-specific subclass. Reusable behaviors should
	be isolated into reusable extension objects, however.
	
	The class attributes listed below control ordering and activation of other extensions. The names of method
	arguments are unimportant; all values are passed positionally.
	"""
	
	provides:Set[str] = set()  # A set of keywords usable in `uses` and `needs` declarations.
	uses:Set[str] = set()  # Used for extension sorting and dependency graphing for optional dependnecies.
	needs:Set[str] = set()  # Used for extension sorting and dependency graphing for required dependencies.
	excludes:Set[str] = set()  # A set of `provides` tags that must not be present for this extension to be usable.
	
	always:bool = False  # If truthy, always enable this extension.
	never:bool = False  # If truthy, never allow this extension to be directly utilized.
	first:bool = False  # Always try to be first: if truthy, become a dependency for all non-first extensions.
	last:bool = False  # Always try to be last: if truthy, include all non-last extensions as a direct dependency.
	
	extensions:Set[str] = set()  # A set of entry_point namespaces to search for related plugin registrations.
	
	def __init__(self, **config):
		"""Executed to configure the extension.
		
		No actions must be performed here, only configuration management.
		
		You can also update the class attributes here.  It only really makes sense to add dependencies.
		"""
		
		super().__init__()
		...
	
	def __call__(self, context, app):
		"""Executed to wrap the application in middleware.
		
		The first argument is the global context class, not request-local context instance.
		
		Accepts a WSGI application as the second argument and must likewise return a WSGI app.
		"""
		...
		
		return app
	
	def start(self, context):
		"""Executed during application startup just after binding the server.
		
		The first argument is the global context class, not request-local context instance.
		
		Any of the actions you wanted to perform during `__init__` you should do here.
		"""
		...
	
	def stop(self, context):
		"""Executed during application shutdown after the last request has been served.
		
		The first argument is the global context class, not request-local context instance.
		"""
		...
	
	def graceful(self, context, **config):
		"""Called when a SIGHUP is sent to the application.
		
		The first argument is the global context class, not request-local context instance.
		
		Allows your code to re-load configuration and your code should close then re-open sockets and files.
		"""
		...
	
	def prepare(self, context):
		"""Executed during request set-up to populate the thread-local `context` instance.
		
		The purpose of the extension ordering is to ensure that methods like these are executed in the correct order.
		"""
		...
	
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
		...
	
	def before(self, context):
		"""Executed after all extension prepare methods have been called, prior to dispatch."""
		...
	
	def after(self, context):
		"""Executed after dispatch has returned and the response populated, prior to anything being sent to the client.
		
		Similar to middleware, the first extension registered has its `after` method called last. Additionally, if
		there is an internal exception, even if that exception will propagate, this callback will be run. Inspect
		`context.response.status` to see if the response was successful.  (Executed in the context of processing an
		exception in most cases where one would be raised.)
		"""
		...
	
	def collect(self, context, handler, bound, args, kw):
		"""Collect, inspect, and potentially mutate the target handler's arguments.
		
		The `args` list and `kw` dictionary may be freely modified, though invalid arguments to the handler will fail.
		"""
		...
	
	def transform(self, context, handler, result):
		"""Transform outgoing values prior to view lookup."""
		...
	
	def done(self, context):
		"""Executed after the entire response has completed generating.
		
		This might seem to duplicate the purpose of `after`; the distinction is with iterable or generator WSGI bodies
		whose processing is deferred until after WebCore has returned. This callback will be executed once iteration
		of the body is complete whereas `after` is executed prior to iteration of the body, but after endpoint
		execution.
		"""
		...
	
	def interactive(self):
		"""Populate an interactive shell."""
		...
		
		return dict()
	
	def inspect(self, context):
		"""Return an object conforming to the inspector panel API."""
		...


class TransactionalExtension:
	"""A more targeted extension example focusing on transaction behaviour within WebCore.
	
	The TransactionExtension must be present in the Application prior to use.
	"""
	
	needs = {'transaction'}
	
	# New! These are callbacks only executed if the TransactionExtension has been configured.
	
	def begin(self, context):
		"""Do the work nessicary to begin a transaction.
		
		This happens during the `prepare` stage if automatic behaviour is indicated, prior to any extensions
		dependency graphed to `need` or `use` yours executing, otherwise, it is only optionally begun upon
		request during the endpoint and response generation lifecycle.
		{move:OtM}, committed prior to the final WSGI application (WebOb) being executed and returned from our own.
		"""
		...
	
	def vote(self, context):
		"""Called to ask extensions if the transaction is still valid."""
		...
	
	def finish(self, context):
		"""Called to complete a transaction, but only if the transaction is valid."""
		...
	
	def abort(self, context):
		"""Called if the vote failed, and the transaction is not valid at time of completion."""
		...
	
	# Understanding behaviour, automatic transaction interactions with existing extension callbacks.
	
	def prepare(self, context):
		"""At this point the underlying machinery has been prepared.
		
		Code may be running under a transaction if automatic behaviour was indicated by configuration of the
		`TransactionExtension`; currently the default is to automatically start a transaction during `prepare` and
		commit on successful HTTP status codes, prior to final delivery of the response content.
		
		{move:TrEx}This has the consequence that in streaming usage, a failure in delivery, or failure in generation (i.e. by
		template engine) of that streamed content, is not an error in the processing of the endpoint itself. If the
		original endpoint indicated success, the transaction is committed.
		"""
		...
	
	def done(self, context):
		"""The last chance to perform any work within an automatic managed transaction."""
		...
