# encoding: utf-8

"""

"""

from web.core.dialects import Dialect, Controller, RESTMethod
from web.core.application import Application
from web.utils.dictionary import adict
from webob import exc as http
from web.core.middleware import middleware, template

from paste.registry import StackedObjectProxy


__all__ = ['Dialect', 'Controller', 'RESTMethod', 'Application', 'config', 'http', 'middleware', 'template', 'config', 'request', 'response', 'cache', 'session']


config = adict(
        response=adict(content_type='text/html', charset='utf8')
    )

request = StackedObjectProxy()
response = StackedObjectProxy()
cache = StackedObjectProxy()
session = StackedObjectProxy()
