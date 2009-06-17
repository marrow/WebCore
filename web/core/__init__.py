# encoding: utf-8

"""

"""

from web.core.dispatch import Controller
from web.core.application import Application
from web.utils.dictionary import adict
from webob import exc as http
from web.core.dispatch import dispatch
from web.core.middleware import template

from paste.registry import StackedObjectProxy


__all__ = ['Controller', 'Application', 'config', 'http', 'dispatch', 'template', 'config', 'request', 'response', 'cache', 'session']


config = adict(
        response=adict(content_type='text/html', charset='utf8')
    )

request = StackedObjectProxy()
response = StackedObjectProxy()
cache = StackedObjectProxy()
session = StackedObjectProxy()
