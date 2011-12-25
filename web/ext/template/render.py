# encoding: utf-8

import os

from functools import wraps

from marrow.templating.core import Engines


_render = Engines()
_lookup = lambda template: resolve(template)[1]
resolve = _render.resolve
registry = []


def _relative(parent):
    parent = _lookup(parent)
    
    def inner(template):
        return os.path.relpath(_lookup(template), os.path.dirname(parent))
    
    return inner


def render(context, template, variables, **extras):
    """Renders a template using marrow.templating while supplementing the given variables with the WebCore context.
    Keyword arguments, if any, are supplied to the renderer as renderer options.
    """
    
    # Do not add any extra data or options to serializers.
    if template[-1] == ':':
        return _render(template, variables, **extras)
    
    data = dict(
            lookup = _lookup,
            relative = _relative(template)
        )
    
    # TODO: Handle callables.
    data.update(context.namespace)
    data.update(variables)
    
    if 'translator' in context:
        extras.setdefault('i18n', context.translator)
    
    return _render(template, data, **extras)
