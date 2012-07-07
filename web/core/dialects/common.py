# encoding: utf-8

"""Basic dispatch routing."""

from api import Dialect
from web.core.http import HTTPNotImplemented


__all__ = ['route']
log = __import__('logging').getLogger(__name__)


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
            raise HTTPNotImplemented('An attempt was made to call a method that can not be routed.')

        part = getattr(last, part, None)

        if not isinstance(part, expects) and isinstance(part, Dialect):
            log.error("Context switching to another dilect from the current RPC dialect is not allowed.")
            raise HTTPNotImplemented('An attempt was made to call a method that can not be routed.')

        if isinstance(part, expects):
            log.debug("Continuing descent through controller structure.")
            parts.pop()
            continue

        if hasattr(part, '__call__') and parts[1:]:
            log.error("Callable method found before reaching the end of the call tree.")
            raise HTTPNotImplemented('An attempt was made to call a method that can not be routed.')

        if hasattr(part, '__call__'):
            parts.pop()
            return part, last

        log.error("An attmpt as made to call an unroutable method: %s", method)
        raise HTTPNotImplemented('An attempt was made to call a method that can not be routed.')
