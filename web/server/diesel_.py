"""Diesel-based WSGI server adapter."""

from diesel.protocols.wsgi import WSGIApplication


def serve(application, host='127.0.0.1', port=8080):
	"""Diesel-based (greenlet) WSGI-HTTP server.
	
	As a minor note, this is crazy. Diesel includes Flask, too.
	"""
	
	# Instantiate the server with a host/port configuration and our application.
	WSGIApplication(application, port=int(port), iface=host).run()
