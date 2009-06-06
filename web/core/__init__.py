# encoding: utf-8

"""

"""

from web.core.dispatch import Controller
from web.core.application import Application
from web.utils.dictionary import adict
from webob import exc as http
from web.core.dispatch import dispatch

from paste.registry import RegistryManager, StackedObjectProxy


__all__ = ['Controller', 'Application', 'config', 'http', 'dispatch', 'request', 'response', 'cache', 'session']


config = adict(
        response=adict(content_type='text/html', charset='utf8')
    )

request = StackedObjectProxy()
response = StackedObjectProxy()
cache = StackedObjectProxy()
session = StackedObjectProxy()
