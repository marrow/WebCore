# encoding: utf-8

"""Eventlet-based WSGI server adapter."""

# ## Imports

from __future__ import unicode_literals, print_function

from eventlet import listen
from eventlet.wsgi import server


# ## Server Adapter

def serve(application, host='127.0.0.1', port=8080):
	"""Eventlet-based WSGI-HTTP server.
	
	For a more fully-featured Eventlet-capable interface, see also [Spawning](http://pypi.python.org/pypi/Spawning/).
	"""
	
	# Instantiate the server with a bound port and with our application.
	server(listen(host, int(port)), application)

