"""The recommended development HTTP server."""

try:
	from waitress import serve as serve_
except ImportError:
	print("You must install the 'waitress' package: pip install waitress")
	raise

from ..core.typing import WSGI, HostBind, PortBind, check_argument_types


def serve(application:WSGI, host:HostBind='127.0.0.1', port:PortBind=8080, threads:int=4, **kw) -> None:
	"""The recommended development HTTP server.
	
	Note that this server performs additional buffering and will not honour chunked encoding breaks.
	
	You may specify specific, explicit `listen` directives to be passed to Waitress' constructor. Doing so will
	prevent automatic addition of `host` and `port` parameters; their values will be silently ignored. Additional
	keyword parameters will be passed through to `waitress.serve` as-is.
	
	This alternate approach allows multiple bindings to be specified, for example, against localhost and the local
	network adapter's IPv4 address, rather than utilizing a potentially over-eager "all interfaces" host bind, or
	to simultaneously serve on the same port across IPv4 and IPv6. E.g.:
	
		app.serve('waitress', listen='127.0.0.1:8080 [::1]:8080')
	
	For a "living" example of this, see `example/basic.py` / `.md` within the WebCore repository. (Useful to silence
	cURL initial connection attempt failure warnings if your system is built with IPv6 support.)
	"""
	
	assert check_argument_types()
	
	if 'listen' not in kw:
		kw = {'host': host, 'port': port, **kw}
	
	kw['threads'] = threads
	kw.setdefault('clear_untrusted_proxy_headers', True)  # We short-circuit a default change to silence a warning.
	
	# Bind and start the server; this is a blocking process.
	serve_(application, **kw)
