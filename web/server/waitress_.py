# encoding: utf-8

"""The recommended development HTTP server."""

# ## Imports

from __future__ import unicode_literals, print_function

try:
	from waitress import serve as serve_
except ImportError:
	print("You must install the 'waitress' package.")
	raise


# ## Server Adapter

def serve(application, host='127.0.0.1', port=8080, threads=4, **kw):
	"""The recommended development HTTP server.
	
	Note that this server performs additional buffering and will not honour chunked encoding breaks.
	"""
	
	# Bind and start the server; this is a blocking process.
	serve_(application, host=host, port=int(port), threads=int(threads), **kw)

