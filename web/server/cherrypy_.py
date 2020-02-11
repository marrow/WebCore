"""CherryPy-based WSGI server adapter."""

from cherrypy.wsgiserver import CherryPyWSGIServer

from ..core.typing import WSGI, HostBind, PortBind


def serve(application:WSGI, host:HostBind='127.0.0.1', port:PortBind=8080) -> None:
	"""CherryPy-based WSGI-HTTP server."""
	
	# Instantiate the server with our configuration and application.
	server = CherryPyWSGIServer((host, int(port)), application, server_name=host)
	
	# Try to be handy as many terminals allow clicking links.
	print("serving on http://{0}:{1}".format(host, port))
	
	# Bind and launch the server; this is a blocking operation.
	try:
		server.start()
	except KeyboardInterrupt:
		server.stop()  # CherryPy has some of its own shutdown work to do.
