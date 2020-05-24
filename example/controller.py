"""Basic class-based demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""

import os

from web.app.static import static


class Another:
	"""A child controller class.
	
	This is "mounted" to the `Root` class, below, as an attribute named `child`; only the attribute name is
	particularly important as it is used as the matched path element during object dispatch descent.
	
	Controller classes effectively represent a template for a directory in a virtual filesystem. Assigning a class to
	an attribute "creates the folder" in the containing class, where callable attributes like methods are "files".
	Dispatch will take care of instantiating any class children, as requested during descent on each request, however,
	because this child controller is statically mounted, no arguments will be passed to the constructor other than the
	current `RequestContext`.
	
	*Important note:* Class instances are request-local. This might not equate to thread local depending on your host
	environment and WSGI server. Try to only rely on what is given to your controller in the context, either passing
	the context itself down, or by extracting the values from it that your controller would need later. Use of global
	state would prevent co-hosting of multiple WebCore applications in a single process, too.
	"""
	
	def __init__(self, context):
		pass  # We don't really care about the context, but can't just omit this method or it'll explode.
	
	def __call__(self):
		"""Executed if the child path is requested specifically.
		
		For example:
		
			curl http://localhost:8080/child/

		"""
		
		return "I'm the baby!"
	
	def eat(self, food:str="pizza"):
		"""
		Executed if this endpoint is accessed.

		For example:
			curl http://localhost:8080/child/eat/
			curl http://localhost:8080/child/eat/sushi/
		"""
		
		return "Yum, I love {food}!".format(food=food)


class Root:
	"""A basic controller class.
	
	This effectively represents the root of the virtual filesystem that is your application. Attributes from this
	object will be treated as child resources, as the default dispatch is object dispatch. For details, see:
	
	https://github.com/marrow/web.dispatch.object#readme
	
	Controller objects are passed the current `RequestContext` object during initialization, it's important to save
	this to `self` or methods won't have access to it when eventually executed. Attributes (properties and methods)
	whose names begin with an underscore are protected and not accessible, similar to the Linux filesystem standard
	of prefixing hidden files and folders with a dot. (This also convienently protects Python magic methods from
	direct web-based execution.)
	
	In order to extend Root into other objects such as Another, you need to register them in class scope with {path element} = {class name}.
	This will make the Another class available to the user as /child via Object dispatching.
	"""
	
	__slots__ = ('_ctx', )  # This is an optimization to tell CPython that our only instance attribute is `_ctx`.
	
	child = Another
	
	def __init__(self, context):
		"""Initialize our controller, either saving the context or getting anything we need from it."""
		self._ctx = context
	
	def __call__(self):
		"""Handle "index" lookups.
		
		This is analogous to an `index.html` file, accessible as the default representation of a folder, that is
		otherwise not accessible as `index.html`. The presence of a `__call__` method makes the controller instance
		itself a valid callable endpoint.
		"""
		
		return "Path: /"
	
	def index(self):
		"""Handle calls to /index.
		
		WebCore 1 treated "index" lookups and the `index` method specially. WebCore 2 does not, freeing the name to be
		used for user-defined endpoints.
		"""
		return "Path: /index"
	
	# Attributes may be assigned statically; these are not callable endpoints but rather static endpoints.
	# WebCore will treat access to these (via /foo, /bar, etc.) as if a callable endpoint was called and the static
	# value returned. This can serve any type of object there is a view registered for.
	string = "Static string!"
	source = open(__file__, 'rb')
	
	# This is a reusable endpoint (like an endpoint factory) serving static files from disk. Serving static files this
	# way is only really useful in development; in production serve them from a production quality front-end server,
	# load balancer, or CDN, such as via Nginx.
	example = static(os.path.dirname(__file__))  # Serve the directory this source file is in. (Don't do this. ;)


if __name__ == '__main__':
	from web.core.application import Application
	
	Application(Root, logging={'level': 'info'}).serve('waitress', threads=15)
