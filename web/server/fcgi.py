# encoding: utf-8

"""A production quality flup-based FastCGI server."""

from __future__ import unicode_literals, print_function

import os

try:
	from flup.server.fcgi import WSGIServer
except ImportError:
	print("You must install the 'flup' package to use FastCGI support.")
	raise


def serve(application, host='127.0.0.1', port=8080, socket=None, multithreaded=True, multiprocess=False, umask=None, multiplexed=False, debug=False):
	"""Basic FastCGI support via flup."""
	
	if not socket:
		bindAddress = (host, int(port))
	else:
		bindAddress = socket
	
	WSGIServer(application, multithreaded=multithreaded, multiprocess=multiprocess, bindAddress=bindAddress, umask=umask, multiplexed=multiplexed, debug=debug).run()
