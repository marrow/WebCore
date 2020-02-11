"""Eventlet-based WSGI server adapter."""

from eventlet import listen
from eventlet.wsgi import server

from ..core.typing import WSGI, HostBind, PortBind


def serve(application:WSGI, host:HostBind='127.0.0.1', port:PortBind=8080) -> None:
	"""Eventlet-based WSGI-HTTP server.
	
	For a more fully-featured Eventlet-capable interface, see also [Spawning](http://pypi.python.org/pypi/Spawning/).
	"""
	
	# Instantiate the server with a bound port and with our application.
	server(listen(str(host), int(port)), application)
