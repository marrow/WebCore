"""Eventlet-based WSGI server adapter."""

from eventlet import listen
from eventlet.wsgi import server


def serve(application, host:str='127.0.0.1', port:int=8080):
	"""Eventlet-based WSGI-HTTP server.
	
	For a more fully-featured Eventlet-capable interface, see also [Spawning](http://pypi.python.org/pypi/Spawning/).
	"""
	
	# Instantiate the server with a bound port and with our application.
	server(listen(str(host), int(port)), application)
