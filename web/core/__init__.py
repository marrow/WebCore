"""The WebCore web nanoframework.

The primary entry point is a WSGI application implementation creatively named `Application`.
"""

from .application import Application
from .util import lazy

# This is to support the web.ext.local extension, and allow for early importing of the variable. The only "superglobal"
# supported inherently by WebCore, and only with the presence of that extension: applications and extensions requiring
# this functionality MUST declare that requirement appropriately, ref: web.ext.local
local = __import__('threading').local()  # Imported this way to avoid an unnecessary hanging reference to 'threading'.

# Symbols exported by this package.
__all__ = (
		'Application',
		'lazy'
		'local',
	)
