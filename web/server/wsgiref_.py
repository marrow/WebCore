# encoding: utf-8

"""Python-standard reference server for development use."""

# ## Imports

from __future__ import unicode_literals, print_function

from wsgiref.simple_server import make_server


# ## Server Adapter

def serve(application, host='127.0.0.1', port=8080):
	"""Python-standard WSGI server for testing purposes.
	
	The additional work performed here is to match the default startup output of "waitress".
	
	This is not a production quality interface and will be have badly under load.
	"""
	
	# Try to be handy as many terminals allow clicking links.
	print("serving on http://{0}:{1}".format(host, port))
	
	# Bind and launch the server; this is a blocking operation.
	make_server(host, port, application).serve_forever()

