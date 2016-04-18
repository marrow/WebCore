# encoding: utf-8

# ## Imports

from __future__ import unicode_literals, print_function

try:
	import tornado.ioloop
	import tornado.httpserver
	import tornado.wsgi
except ImportError:
	print("You must install the 'tornado' package.")
	raise


# ## Server Adapter

def serve(application, host='127.0.0.1', port=8080, **options):
	"""Tornado's HTTPServer.
	
	This is a high quality asynchronous server with many options.  For details, please visit:
	
		http://www.tornadoweb.org/en/stable/httpserver.html#http-server
	"""
	
	# Wrap our our WSGI application (potentially stack) in a Tornado adapter.
	container = tornado.wsgi.WSGIContainer(application)
	
	# Spin up a Tornado HTTP server using this container.
	http_server = tornado.httpserver.HTTPServer(container, **options)
	http_server.listen(int(port), host)
	
	# Start and block on the Tornado IO loop.
	tornado.ioloop.IOLoop.instance().start()

