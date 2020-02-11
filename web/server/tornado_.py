try:
	import tornado.ioloop
	import tornado.httpserver
	import tornado.wsgi
except ImportError:
	print("You must install the 'tornado' package.")
	raise


from ..core.typing import WSGI, HostBind, PortBind


def serve(application:WSGI, host:HostBind='127.0.0.1', port:PortBind=8080, **options) -> None:
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
