# encoding: utf-8

"""Python-standard reference servers for development use."""

# ## Imports

from __future__ import unicode_literals, print_function

from wsgiref.handlers import CGIHandler
from wsgiref.simple_server import make_server


# ## Production Warning

# We let people know it's a bad idea to use these in production.
if not __debug__:
	import warnings
	warnings.warn("Use of standard library reference servers in production is discouraged.", RuntimeWarning)


# ## Server Adapters

def simple(application, host='127.0.0.1', port=8080):
	"""Python-standard WSGI-HTTP server for testing purposes.
	
	The additional work performed here is to match the default startup output of "waitress".
	
	This is not a production quality interface and will be have badly under load.
	"""
	
	# Try to be handy as many terminals allow clicking links.
	print("serving on http://{0}:{1}".format(host, port))
	
	# Bind and launch the server; this is a blocking operation.
	make_server(host, int(port), application).serve_forever()


def cgi(application):
	"""Python-standard WSGI-CGI server for testing purposes.
	
	This is not a production quality interface and will behave badly under load. Python-as-CGI is not a very good way
	to deploy any application. (Startup/shutdown on every request is a PHP problem.) This _can_ be useful as a
	diagnostic tool in development, however.
	"""
	
	if not __debug__:
		warnings.warn("Interactive debugging and other persistence-based processes will not work.")
	
	# Instantiate the handler and begin bridging the application.
	CGIHandler().run(application)


def iiscgi(application):
	"""A specialized version of the reference WSGI-CGI server to adapt to Microsoft IIS quirks.
	
	This is not a production quality interface and will behave badly under load.
	"""
	try:
		from wsgiref.handlers import IISCGIHandler
	except ImportError:
		print("Python 3.2 or newer is required.")
	
	if not __debug__:
		warnings.warn("Interactive debugging and other persistence-based processes will not work.")
	
	IISCGIHandler().run(application)



