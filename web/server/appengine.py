# encoding: utf-8

"""Python-standard reference servers for development use."""

# ## Imports

from __future__ import unicode_literals

import warnings

from google.appengine.ext.webapp.util import run_wsgi_app


# ## Server Adapter

def appengine(application):
	"""Google App Engine adapter, CGI.
	
	Note: This adapter is essentially untested, and likely duplicates the `cgiref` adapter.
	"""
	
	warnings.warn("Interactive debugging and other persistence-based processes will not work.")
	
	# Bridge the current CGI request.
	run_wsgi_app(application)

