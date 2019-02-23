"""Gevent-based WSGI server adapter."""

from gevent.pywsgi import WSGIServer


def serve(application, host='127.0.0.1', port=8080):
	"""Gevent-based WSGI-HTTP server."""
	
	# Instantiate the server with a host/port configuration and our application.
	WSGIServer((host, int(port)), application).serve_forever()
