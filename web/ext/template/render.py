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
    
    Template lookup can be overridden on a per-package basis, configured thusly:
    
    web.template.path:
        web.auth.template: myapp.template.auth
    
    You can also directly manipulate the context.render.path dictionary.
    
    With the above configuration as an example, a request to render 'web.auth.template.foo' will look in:
    
        myapp.template.auth/foo.html
        web.auth.template/foo.html
    
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
    
    path = getattr(context.render, 'path', dict())
    if not path:
        return _render(template, data, **extras)
    
    format = ''
    if ':' in template:
        format, _, template = template.partition(':')
        format = format + _
    
    # Find all matching overrides, preferring deeper ones.
    matched = [i for i in path if template.startswith(i)]
    matched.sort(lambda a, b: len(b) - len(a))
    
    result = None
    for i in matched:
        tmpl = format + template.replace(i, path[i])
        try:
            result = _render(tmpl, data, **extras)
        except (ImportError, IOError, ValueError):
            continue
        else:
            break
    
    if not result:
        result = _render(template, data, **extras)
    
    return result
