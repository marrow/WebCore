# encoding: utf-8

from web.core import Dialect
from web.core.http import HTTPNotImplemented


__all__ = ['RoutingError', 'route']
log = __import__('logging').getLogger(__name__)


class RoutingError(HTTPNotImplemented):
    def __init__(self):
        HTTPNotImplemented.__init__(self, 'An attempt was made to call a method that can not be routed.')


def route(root, method, expects):
    last = None
    part = root
    parts = method.split('.')
    parts.reverse()
    
    while True:
        last = part
        part = parts[-1]
        
        log.debug("Looking for %r attribute of %r.", part, last)
        
        if part.startswith('_'):
            log.error("An attempt was made to route a private object: %s", method)
            raise RoutingError
        
        part = getattr(last, part, None)
        
        if not isinstance(part, expects) and isinstance(part, Dialect):
            log.error("Context switching to another dialect from the current RPC dialect is not allowed.")
            raise RoutingError
        
        if isinstance(part, expects):
            log.debug("Continuing descent through controller structure.")
            parts.pop()
            continue
        
        if callable(part) and parts[1:]:
            log.error("Callable method found before reaching the end of the call tree.")
            raise RoutingError
        
        if callable(part):
            parts.pop()
            return part, last
        
        log.error("An attempt was made to call an unroutable method: %s", method)
        raise RoutingError
