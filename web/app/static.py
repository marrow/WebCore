# encoding: utf-8

"""Basic static file delivery mechanism."""

# ## Imports

from __future__ import unicode_literals

from os.path import abspath, normpath, exists, isfile, join as pathjoin, basename
from webob.exc import HTTPForbidden, HTTPNotFound


# ## Module Globals

# A standard logging object.
log = __import__('logging').getLogger(__name__)


# ## Static File Endpoint

def static(base, mapping=None, far=('js', 'css', 'gif', 'jpg', 'jpeg', 'png', 'ttf', 'woff')):
	"""Serve files from disk.
	
	This utility endpoint factory is meant primarily for use in development environments; in production environments
	it is better (more efficient, secure, etc.) to serve your static content using a front end load balancer such as
	Nginx.
	
	The first argument, `base`, represents the base path to serve files from. Paths below the attachment point for
	the generated endpoint will combine this base path with the remaining path elements to determine the file to
	serve.
	
	The second argument is an optional dictionary mapping filename extensions to template engines, for cooperation
	with the TemplateExtension.  (See: https://github.com/marrow/template)  The result of attempting to serve a
	mapped path is a 2-tuple of `("{mapping}:{path}", dict())`. For example, to render all `.html` files as Mako
	templates, you would attach something like the following:
	
		class Root:
			page = static('/path/to/static/pages', dict(html='mako'))
	
	By default the "usual culprits" are served with far-futures cache expiry headers. If you wish to change the
	extensions searched just assign a new `far` iterable.  To disable, assign any falsy value.
	"""
	
	base = abspath(base)
	
	@staticmethod
	def static_handler(context, *parts, **kw):
		path = normpath(pathjoin(base, *parts))
		
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

