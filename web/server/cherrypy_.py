# encoding: utf-8

"""CherryPy-based WSGI server adapter."""

# ## Imports

from __future__ import unicode_literals, print_function

from cherrypy.wsgiserver import CherryPyWSGIServer


# ## Server Adapter

def serve(application, host='127.0.0.1', port=8080):
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

