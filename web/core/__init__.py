# Expose these as importable from the top-level `web.core` namespace.
from .application import Application
from .util import lazy

__all__ = ['local', 'Application', 'lazy']  # Symbols exported by this package.

# This is to support the web.ext.local extension, and allow for early importing of the variable.
local = __import__('threading').local()
