# encoding: utf-8

import web.core
from routes.mapper import Mapper


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
            raise web.core.http.HTTPNotFound()
        
        parts = result.get('controller').split('.') if 'controller' in result else []
        
        controller = self
        
        for part in parts:
            if not hasattr(controller, part):
                raise web.core.http.HTTPNotFound()
            
            controller = getattr(controller, part)
        
        method = result.get('action', None)
        
        if method is None:
            raise web.core.http.HTTPNotFound()
        
        try:
            del result['controller']
        
        except:
            pass
        
        del result['action']
        
        return getattr(controller, method)(**result)
