"""Gevent-based WSGI server adapter."""

from gevent.pywsgi import WSGIServer

from ..core.typing import WSGI, HostBind, PortBind, check_argument_types


def serve(application:WSGI, host:HostBind='127.0.0.1', port:PortBind=8080) -> None:
	"""Gevent-based WSGI-HTTP server."""
	
	assert check_argument_types()
	
	# Instantiate the server with a host/port configuration and our application.
	WSGIServer((str(host), int(port)), application).serve_forever()
