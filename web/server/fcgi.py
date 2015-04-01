# encoding: utf-8

"""A production quality flup-based FastCGI server."""

from __future__ import unicode_literals, print_function

import os

try:
	from flipflop import WSGIServer
except ImportError:
	print("You must install the 'flipflop' package to use FastCGI support.")
	raise


def serve(application, host='127.0.0.1', port=8080, socket=None):
	"""Basic FastCGI support via flipflop, an extract of FastCGI protocol support from flup."""
	
	if not socket:
		socket = (host, int(port))
		# ensure_port_cleanup([sock])
	
	os.environ['FCGI_WEB_SERVER_ADDRS'] = socket
	
	WSGIServer(application).run()
