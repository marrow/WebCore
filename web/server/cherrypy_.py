"""CherryPy-based WSGI server adapter."""

from cherrypy.wsgiserver import CherryPyWSGIServer

from ..core.typing import WSGI, HostBind, PortBind, check_argument_types


def serve(application:WSGI, host:HostBind='127.0.0.1', port:PortBind=8080) -> None:
	"""CherryPy-based WSGI-HTTP server."""
	
	assert check_argument_types()
	
	host = str(host)
	
	# Instantiate the server with our configuration and application.
	server = CherryPyWSGIServer((host, int(port)), application, server_name=host)
	
	# Try to be handy as many terminals allow clicking links.
	print(f"serving on http://{host!s}:{port!s}")
	
	# Bind and launch the server; this is a blocking operation.
	try:
		server.start()
	except KeyboardInterrupt:
		server.stop()  # CherryPy has some of its own shutdown work to do.
		raise  # Continue propagation.
