# encoding: utf-8

import web

from routes.mapper import Mapper
from web.core.http import HTTPNotFound


__all__ = ['RoutingController']


class RoutingController(web.core.Dialect):
    """Routes-based dispatch.

    Subclass and override __init__ to define your routes.  E.g.

        class RootController(RoutesController):
            def __init__(self):
                super(RootController, self).__init__()
                self._map.connect(None, "/error/{method}/{id}, action="error")
                # ...

    Methods to be called are named attributes or named attributes of
    nested controllers.  Nested controllers may be simple new-style
    class instances; they do not need to inherit from Dialect or
    RoutesController.

    In your route definitions, 'action' refers to the method,
    'controller' optionally refers to a nested controller and you can
    use dot notation to refer to sub-sub controllers, etc.
    """
    def __init__(self):
        self._map = Mapper()
        self._map.minimization = False

    def __call__(self, request):
        result = self._map.match(environ=request.environ)

        if not result:
            raise HTTPNotFound()

        parts = result.get('controller').split('.') if 'controller' in result else []

        controller = self

        for part in parts:
            if not hasattr(controller, part):
                raise HTTPNotFound()

            controller = getattr(controller, part)

        method = result.get('action', None)
        result.pop('controller', None)
        del result['action']

        m = getattr(controller, method, None)

        if not m:
            raise HTTPNotFound()

        return m(**result)
