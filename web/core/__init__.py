# encoding: utf-8

# ## Imports

from threading import local as __local

# Expose these as importable from the top-level `web.core` namespace.

from .application import Application
from .util import lazy


# ## Module Globals

# This is to support the web.ext.local extension, and allow for early importing of the variable.
local = __local()

