# encoding: utf-8

from __future__ import unicode_literals

from os.path import abspath, normpath, exists, isfile, join as pathjoin, basename
from webob.exc import HTTPForbidden, HTTPNotFound
from web.core.compat import ldump


log = __import__('logging').getLogger(__name__)


def static(base, mapping=None):
	base = abspath(base)
	
	@staticmethod
	def static_handler(context, *parts, **kw):
		path = normpath(pathjoin(base, *parts))
		
		log.debug("%d:Attempting to serve static file.%s", id(context.request), ldump(
				base = base,
				path = path
			))
		
		if not path.startswith(base):
			raise HTTPForbidden("Cowardly refusing to violate base path policy.")
		
		if not exists(path):
			raise HTTPNotFound()
		
		if not isfile(path):
			raise HTTPForbidden("Cowardly refusing to open a non-file.")
		
		if mapping:
			# This handles automatic template rendering.  'Cause why not?
			_, _, extension = basename(path).partition('.')
			if extension in mapping:
				return mapping[extension] + ':' + path, dict()
		
		return open(path, 'rb')
	
	return static_handler
