"""A production quality flup-based FastCGI server."""

try:
	from flup.server.fcgi import WSGIServer
except ImportError:
	print("You must install a 'flup' package such as 'flup6' to use FastCGI support.")
	raise


def serve(application, host='127.0.0.1', port=8080, socket=None, **options):
	"""Basic FastCGI support via flup.
	
	This web server has many, many options. Please see the Flup project documentation for details.
	"""
	
	# Allow either on-disk socket (recommended) or TCP/IP socket use.
	if not socket:
		bindAddress = (host, int(port))
	else:
		bindAddress = socket
	
	# Bind and start the blocking web server interface.
	WSGIServer(application, bindAddress=bindAddress, **options).run()
