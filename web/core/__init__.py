# encoding: utf-8

import sys

from webob import exc as http
from paste.registry import StackedObjectProxy
from web import release
from web.core.application import Application
from web.core.dialects import Dialect, Controller, HTTPMethod, RESTMethod
from web.core.middleware import middleware
from web.utils import URLGenerator
from marrow.util.bunch import Bunch


__all__ = [
        'Application', 'Dialect', 'Controller', 'HTTPMethod', 'RESTMethod',
        'http', 'i18n', 'middleware'
        'config', 'request', 'response', 'cache', 'session', 'translator', 'namespace'
    ]


config = Bunch()

request = StackedObjectProxy(name="request")
response = StackedObjectProxy(name="response")
cache = StackedObjectProxy(name="cache")
session = StackedObjectProxy(name="session")

translator = StackedObjectProxy(name="translator")

url = URLGenerator()

namespace = Bunch(
        web=Bunch(
                request=request,
                response=response,
                cache=cache,
                session=session,
                i18n=translator,
                release=release,
                config=config,
                url=url
            )
    )

# To allow 'from web.core.http import ...' statements, we have to register web.core.http as a module.
sys.modules['web.core.http'] = http
