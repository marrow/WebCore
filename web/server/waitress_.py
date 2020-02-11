"""The recommended development HTTP server."""

try:
	from waitress import serve as serve_
except ImportError:
	print("You must install the 'waitress' package.")
	raise

from ..core.typing import WSGI, HostBind, PortBind


def serve(application:WSGI, host:HostBind='127.0.0.1', port:PortBind=8080, threads:int=4, **kw) -> None:
	"""The recommended development HTTP server.
	
	Note that this server performs additional buffering and will not honour chunked encoding breaks.
	"""
	
	# Bind and start the server; this is a blocking process.
	serve_(application, host=str(host), port=int(port), threads=int(threads), **kw)
