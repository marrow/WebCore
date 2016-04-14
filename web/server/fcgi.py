# encoding: utf-8

"""A production quality flup-based FastCGI server."""

from __future__ import unicode_literals, print_function

try:
	from flup.server.fcgi import WSGIServer
except ImportError:
	print("You must install the 'flup' package to use FastCGI support.")
	raise


def serve(application, host='127.0.0.1', port=8080, socket=None, **options):
	"""Basic FastCGI support via flup.
	
	This web server has many, many options. Please see the Flup project documentation for details.
	"""
	
	if not socket:
		bindAddress = (host, int(port))
	else:
		bindAddress = socket
	
	WSGIServer(application, bindAddress=bindAddress, **options).run()

