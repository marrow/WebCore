# encoding: utf-8

"""A WSGIRef-based local development server using the Python standard library.

Warning: this server is not production quality.  It *will* behave badly under load.
"""

from __future__ import unicode_literals, print_function

from wsgiref.simple_server import make_server


def serve(application, host='127.0.0.1', port=8080):
	"""Basic built-in WSGI server.
	
	The additional work performed here is to match the default startup output of "waitress".
	"""
	
	print("serving on http://{0}:{1}".format(host, port))
	
	try:
		make_server(host, port, application).serve_forever()
	except KeyboardInterrupt:
		pass
