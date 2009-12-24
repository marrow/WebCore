# encoding: utf-8

"""

"""

import sys
from web import release
from web.core.dialects import Dialect, Controller, RESTMethod
from web.core.application import Application
from web.utils.dictionary import adict
from webob import exc as http
from web.core.middleware import middleware

from paste.registry import StackedObjectProxy


__all__ = [
        'Application', 'Dialect', 'Controller', 'RESTMethod',
        'http', 'i18n', 'middleware'
        'config', 'request', 'response', 'cache', 'session', 'translator', 'namespace']


config = adict()

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

# To allow 'from web.core.http import ...' statements, we have to register web.core.http as a module.
sys.modules['web.core.http'] = http
