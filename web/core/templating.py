# encoding: utf-8

import os

from functools import wraps
from marrow.templating.core import Engines
from marrow.util.compat import unicode
from web.core import request, response


__all__ = ['resolve', 'registry', 'render', 'template', 'TemplatingMiddleware']
log = __import__('logging').getLogger(__name__)

_render = Engines()
_lookup = lambda template: resolve(template)[1]
resolve = _render.resolve
registry = []


def _relative(parent):
    parent = _lookup(parent)

    def inner(template):
        return os.path.relpath(_lookup(template), os.path.dirname(parent))
    return inner


def render(template, variables, **extras):
    """Renders a template using marrow.templating while supplementing the
    given variables with the WebCore globals. Keyword arguments, if any, are
    supplied to the renderer as renderer options.
    """

    # Do not add any extra data or options to serializers
    if not template.endswith(':'):
        data = dict(
                lookup=_lookup,
                relative=_relative(template)
            )

        for i in registry:
            if callable(i):
                data.update(i())
            else:
                data.update(i)

        data.update(variables)
        variables = data

        if request and 'web.translator' in request.environ:
            extras.setdefault('i18n', request.environ['web.translator'])

    return _render(template, variables, **extras)


def template(template, **extras):
    """Decorates a function to output a rendered template, just like a
    controller method. Keyword arguments, if any, are supplied to the renderer
    as renderer options.
    """
    def outer(func):
        @wraps(func)
        def inner(*args, **kw):
            result = func(*args, **kw)
            if not isinstance(result, dict):
                return result

            return render(template, result, **extras)[1]

        return inner

    return outer


class TemplatingMiddleware(object):
    def __init__(self, application, config=dict(), **kw):
        self.config = config.copy()
        self.config.update(kw)
        self.application = application

        resolve.default = config.get('web.templating.engine', 'genshi')

    def __call__(self, environ, start_response):
        result = self.application(environ, start_response)

        # Bail if the returned value is not a tuple.
        if not isinstance(result, tuple):
            return result

        if len(result) == 2:
            template, data, extras = result + (dict(),)
        elif len(result) == 3:
            template, data, extras = result

        if not isinstance(template, basestring) or not isinstance(extras, dict):
            raise TypeError("Invalid tuple values returned to TemplatingMiddleware.")

        response.content_type, output = render(template, data, **extras)

        if isinstance(response.content_type, unicode):
            response.content_type = response.content_type.encode('iso-8859-1')

        if isinstance(output, str):
            response.body = output
        elif isinstance(output, unicode):
            response.unicode_body = output

        return response(environ, start_response)
