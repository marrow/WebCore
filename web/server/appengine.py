"""Python-standard reference servers for development use."""

import warnings

from google.appengine.ext.webapp.util import run_wsgi_app


def appengine(application):
	"""Google App Engine adapter, CGI.
	
	Note: This adapter is essentially untested, and likely duplicates the `cgiref` adapter.
	"""
	
	warnings.warn("Interactive debugging and other persistence-based processes will not work.")
	
	# Bridge the current CGI request.
	run_wsgi_app(application)
