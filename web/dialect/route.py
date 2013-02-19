# encoding: utf-8

import re

from inspect import isclass
from functools import wraps
from collections import namedtuple

from marrow.util.compat import unicode
from marrow.wsgi.exceptions import HTTPNotFound


re_type = type(re.compile(""))


def route(route, router=None):
    def inner(func):
        if router:
            # Immediate routing declaration; mostly for testing.
            router.register(route, func)
        else:
            # Deferred routing declaration.
            func.__route__ = route
        return func

    return inner


class Router(object):
    def __init__(self):
        self.routes = list()

    def register(self, route, obj):
        parsed = self.parse(route)

        print("registering", route, parsed)

        routes = self.routes

        for element in parsed:
            for i, (route, children) in enumerate(routes):
                if route is not element:
                    continue

                if not isinstance(children, list):
                    children = [(None, children)]
                    routes[i] = (route, children)

                routes = children
                break

            else:
                routes.append((element, obj))

    def parse(self, route):
        parts = route.lstrip('/').split('/')

        for i, part in enumerate(parts):
            if '{' not in part:
                continue

            elif '}' not in part:
                raise ValueError("Route match must not contain forward slashes.")

            sub = list()

            while part:
                prefix, _, match = part.partition('{')
                name, _, part = match.partition('}')
                sub.append(prefix)

                name, _, regex = name.partition(':')
                sub.append('(?P<%s>%s)' % (name, regex or r'[^/]+'))

            parts[i] = re.compile(''.join(sub))

        return parts

    def route(self, path):
        routes = self.routes
        path = path.lstrip('/').split('/') + [None]
        match = dict()

        for i, element in enumerate(path):
            for route, children in routes:
                if isinstance(route, re_type):
                    matched = route.match(element)
                    if not matched: continue
                    match.update(matched.groupdict())

                elif route != element:
                    continue

                if not isinstance(children, list):
                    return children, [i for i in path[i+1:] if i is not None], match

                routes = children
                break

            else:
                raise ValueError("Could not find route to satisfy path.")

        raise ValueError("Could not find route to satisfy path.")


class RoutingDialect(object):
    def __init__(self, config):
        print("CALLED")
        super(RoutingDialect, self).__init__()

    def __call__(self, context, root):
        log = context.log
        path = context.request.remainder

        # Capture and eliminate the final, empty path element.
        # If present there was a trailing slash in the original path, which we don't care about.
        if path[-1:] == ['']:
            path.pop()

        path = unicode(path)

        __import__('pprint').pprint((path, root))

        if isclass(root):
            # Build a strongly-bound router for this object.
            # If you add new routes during method calls, pass self.__router__ as a second argument to
            # the @route decorator to ensure your route is discoverable.
            root = root(context)

            if not hasattr(root, '__router__'):
                router = root.__router__ = Router()

                for name in (i for i in dir(root) if not i.startswith('_')):
                    obj = getattr(root, name)
                    route =  getattr(obj, '__route__', None)
                    if not route: continue
                    router.register(route, obj)

        try:
            target, remainder, args = router.route(path)
            remainder = '/' + '/'.join(remainder)
            context.request.kwargs.update(args)

        except ValueError as e:
            raise HTTPNotFound()

        yield path[:len(path)-len(remainder)].split('/'), target, not hasattr(target, '__dialect__')


if __name__ == '__main__':
    router = Router()

    @route('/', router)
    def index(ctx):
        print("index")

    @route('/create', router)
    def create(ctx):
        pass

    @route('/{id}', router)
    def show(ctx, id):
        pass

    @route('/{id}/modify', router)
    def modify(ctx, id):
        pass

    @route('/{id}/delete', router)
    def delete(ctx, id):
        pass

    print()
    __import__('pprint').pprint(router.routes)
    print()

    for i in ('/', '/create', '/27', '/42/modify', '/64/delete', '/64/delete/confirm', '/create/diz', '/bob'):
        print(i, '\t\t' if len(i) < 7 else '\t', router.route(i))

    from marrow.wsgi.objects.path import Path
    from marrow.util.bunch import Bunch

    class Context(object):
        log = None

        def __init__(self, path):
            self.request = Bunch(remainder=Path(path))

    class Root(object):
        def __init__(self, context):
            self.ctx = context

        @route('/')
        def index(self):
            print("index")

        @route('/create')
        def create(self):
            print("create")

    print()

    router = RoutingDialect(None)
    context = Context('/create')
    for consumed, target, last in router(context, Root):
        print(repr(consumed), target, last)

