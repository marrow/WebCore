# encoding: utf-8

from threading import local as __local

from .application import Application
from .util import lazy


# This is to support the web.ext.local extension, and allow for early importing of the variable.
local = __local()

