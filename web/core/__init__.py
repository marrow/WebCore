# encoding: utf-8

"""

"""

from web import release
from web.core.dialects import Dialect, Controller, RESTMethod
from web.core.application import Application
from web.utils.dictionary import adict
from webob import exc as http
from web.core.middleware import middleware

from paste.registry import StackedObjectProxy


__all__ = ['Dialect', 'Controller', 'RESTMethod', 'Application', 'config', 'http', 'middleware', 'i18n', 'config', 'request', 'response', 'cache', 'session']


config = adict(
        response=adict(content_type='text/html', charset='utf8')
    )

request = StackedObjectProxy(name="request")
response = StackedObjectProxy(name="response")
cache = StackedObjectProxy(name="cache")
session = StackedObjectProxy(name="session")

translator = StackedObjectProxy(name="translator")

namespace = dict(
        web = adict(
                request = request,
                response = response,
                cache = cache,
                session = session,
                i18n = translator,
                release = release
            )
    )
