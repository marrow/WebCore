# encoding: utf-8

from __future__ import unicode_literals, print_function

from wsgiref.simple_server import make_server


def serve(application, host='127.0.0.1', port=8080):
	"""Python standard WSGI server for testing purposes.
	
	The additional work performed here is to match the default startup output of "waitress".

	This is not a production quality interface and will be have badly under load.
	"""
	
	print("serving on http://{0}:{1}".format(host, port))
	
	try:
		make_server(host, port, application).serve_forever()
	except KeyboardInterrupt:
		pass

