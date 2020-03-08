"""A rudimentary static file delivery mechanism with support for extension-based view mapping.

The single callable provided is a factory for a function usable as a callable endpoint under WebCore dispatch.
Invoking this produces the object you use to serve files from the targeted base path. It is usable in nearly any
context: as a bare function endpoint, a static method under object dispatch, etc.

This utility endpoint factory is intended primarily for use in development environments; in production environments it
is better (more efficient, secure, reliable, etc.) to serve your static content using a FELB (Front-End Load Balancer)
such as Nginx, Apache, or Lighttpd. As a shortcut aid to development, it has not been extensively battle-tested
against abuse by malicious actors when exposed directly to the internet.

A configuration parameter for the base extension is provided to permit use of X-Sendfile or Nginx X-Accel-Redirect
support when delivering named file handle content. The latter requires knowledge of the base internal path to use.

As an example of use, using object dispatch, you might construct an "application root" ("entry point") object such as:

	class MyAwesomeApplication:
		public = static('static')

If served, any request to a path below `/public/` will attempt to open a file below `./static/`, that is, the `static`
directory below the application process' current working directory. As no mapping was provided, this will always
either result in an HTTPError or an open handle to the appropriate on-disk file for view processing and delivery to
the requesting client.

"""

from logging import getLogger, Logger
from os.path import abspath, normpath, exists, isfile, join as pathjoin, basename

from webob.exc import HTTPForbidden, HTTPNotFound


def static(base, mapping=None, far=('js', 'css', 'gif', 'jpg', 'jpeg', 'png', 'ttf', 'woff')):
	"""Factory to produce a callable capable of resolving and serving static assets (files) from disk.
	
	The first argument, `base`, represents the base path to serve files from. Paths below the attachment point for
	the generated endpoint will combine this base path with the remaining path elements to determine the file to
	serve.
	
	The second argument is an optional mapping of filename extensions to the first component of the 2-tuple return
	value, for cooperation with views matching tuple types.  The result of attempting to serve a mapped path is a
	2-tuple of `(f'{mapping}:{path}', )`
	
	with the TemplateExtension.  (See: https://github.com/marrow/template)  The result of attempting to serve a
	mapped path is a 2-tuple of `("{mapping}:{path}", dict())`. For example, to render all `.html` files as Mako
	templates, you would attach something like the following:
	
		class Root:
			page = static('/path/to/static/pages', dict(html='mako'))
	
	By default the "usual culprits" are served with far-futures cache expiry headers. If you wish to change the
	extensions searched just assign a new `far` iterable.  To disable, assign any falsy value.
	"""
	
	base: str = abspath(base)
	log: Logger = getLogger(__name__)
	
	@staticmethod
	def static_handler(context, *parts, **kw):
		path: str = normpath(pathjoin(base, *parts))
		
		if __debug__:
			log.debug("Attempting to serve static file.", extra=dict(
					request = id(context),
					base = base,
					path = path
				))
		
		if not path.startswith(base):  # Ensure we only serve files from the allowed path.
			raise HTTPForbidden("Cowardly refusing to violate base path policy." if __debug__ else None)
		
		if not exists(path):  # Do the right thing if the file doesn't actually exist.
			raise HTTPNotFound()
		
		if not isfile(path):  # Only serve normal files; no UNIX domain sockets, FIFOs, etc., etc.
			raise HTTPForbidden("Cowardly refusing to open a non-file." if __debug__ else None)
		
		if far and path.rpartition('.')[2] in far:
			context.response.cache_expires = 60*60*24*365
		
		if mapping:  # Handle the mapping of filename extensions to 2-tuples. 'Cause why not?
			_, _, extension = basename(path).partition('.')
			if extension in mapping:
				return mapping[extension] + ':' + path, dict()
		
		return open(path, 'rb')
	
	return static_handler
