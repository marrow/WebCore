# encoding: utf-8

"""Gevent-based WSGI server adapter."""

# ## Imports

from __future__ import unicode_literals, print_function

from gevent.pywsgi import WSGIServer


# ## Server Adapter

def serve(application, host='127.0.0.1', port=8080):
	"""Gevent-based WSGI-HTTP server."""
	
	# Instantiate the server with a host/port configuration and our application.
	WSGIServer((host, int(port)), application).serve_forever()

