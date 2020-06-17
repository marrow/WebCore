"""Python-standard reference servers for development use."""

import warnings

from google.appengine.ext.webapp.util import run_wsgi_app

from ..core.typing import WSGI, check_argument_types


def appengine(application:WSGI) -> None:
	"""Google App Engine adapter, CGI.
	
	Note: This adapter is essentially untested, and likely duplicates the `cgiref` adapter.
	"""
	
	assert check_argument_types()
	
	warnings.warn("Interactive debugging and other persistence-based processes will not work.", RuntimeWarning)
	
	# Bridge the current CGI request.
	run_wsgi_app(application)
