"""A production quality flup-based FastCGI server."""

try:
	from flup.server.fcgi import WSGIServer
except ImportError:
	print("You must install a 'flup' package such as 'flup6' to use FastCGI support: pip install flup6")
	raise

from ..core.typing import WSGI, HostBind, PortBind, DomainBind, check_argument_types


def serve(application:WSGI, host:HostBind='127.0.0.1', port:PortBind=8080, socket:DomainBind=None, **options) -> None:
	"""Basic FastCGI support via flup.
	
	This web server has many, many options. Please see the Flup project documentation for details.
	"""
	
	assert check_argument_types()
	
	# Allow either on-disk socket (recommended) or TCP/IP socket use.
	bind = socket if socket else (str(host), int(port))
	
	# Bind and start the blocking web server interface.
	WSGIServer(application, bindAddress=bindAddress, **options).run()
