"""Diesel-based WSGI server adapter."""

from diesel.protocols.wsgi import WSGIApplication

from ..core.typing import WSGI, HostBind, PortBind, check_argument_types


def serve(application:WSGI, host:HostBind='127.0.0.1', port:PortBind=8080) -> None:
	"""Diesel-based (greenlet) WSGI-HTTP server.
	
	As a minor note, this is crazy. Diesel includes Flask, too.
	"""
	
	assert check_argument_types()
	
	# Instantiate the server with a host/port configuration and our application.
	WSGIApplication(application, port=int(port), iface=str(host)).run()
