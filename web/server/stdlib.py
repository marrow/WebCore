"""Python-standard reference servers for development use."""

from wsgiref.handlers import CGIHandler, IISCGIHandler
from wsgiref.simple_server import make_server

from ..core.typing import WSGI, HostBind, PortBind


# We let people know it's a bad idea to use these in production.
if not __debug__:
	import warnings
	warnings.warn("Use of standard library reference servers in production is discouraged.", RuntimeWarning)


def simple(application:WSGI, host:HostBind='127.0.0.1', port:PortBind=8080) -> None:
	"""Python-standard WSGI-HTTP server for testing purposes.
	
	The additional work performed here is to match the default startup output of "waitress".
	
	This is not a production quality interface and will be have badly under load.
	"""
	
	# Try to be handy as many terminals allow clicking links.
	print("serving on http://{0}:{1}".format(host, port))
	
	# Bind and launch the server; this is a blocking operation.
	make_server(str(host), int(port), application).serve_forever()


def cgi(application:WSGI) -> None:
	"""Python-standard WSGI-CGI server for testing purposes.
	
	This is not a production quality interface and will behave badly under load. Python-as-CGI is not a very good way
	to deploy any application. (Startup/shutdown on every request is a PHP problem.) This _can_ be useful as a
	diagnostic tool in development, however.
	"""
	
	if not __debug__:
		warnings.warn("Interactive debugging and other persistence-based processes will not work within this environment.", RuntimeWarning)
	
	# Instantiate the handler and begin bridging the application.
	CGIHandler().run(application)


def iiscgi(application:WSGI) -> None:
	"""A specialized version of the reference WSGI-CGI server to adapt to Microsoft IIS quirks.
	
	This is not a production quality interface and will behave badly under load.
	"""
	try:
		from wsgiref.handlers import IISCGIHandler
	except ImportError:
		print("Python 3.2 or newer is required.")
	
	if not __debug__:
		warnings.warn("Interactive debugging and other persistence-based processes will not work within this environment.", RuntimeWarning)
	
	IISCGIHandler().run(application)
