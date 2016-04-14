# encoding: utf-8

from __future__ import unicode_literals, print_function

try:
	import tornado.ioloop
	import tornado.httpserver
	import tornado.wsgi
except ImportError:
	print("You must install the 'tornado' package.")
	raise


def serve(application, host='127.0.0.1', port=8080, **options):
	"""Tornado's HTTPServer.
	
	This is a high quality asynchronous server with many options.  For details, please visit:
	
		http://www.tornadoweb.org/en/stable/httpserver.html#http-server
	"""
	
	container = tornado.wsgi.WSGIContainer(application)
	
	http_server = tornado.httpserver.HTTPServer(container, **options)
	http_server.listen(int(port), host)
	
	tornado.ioloop.IOLoop.instance().start()

