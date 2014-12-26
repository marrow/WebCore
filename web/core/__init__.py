# encoding: utf-8

# This is to support the web.ext.local extension, and allow for early importing of the variable.

from threading import local as __local


local = __local()
