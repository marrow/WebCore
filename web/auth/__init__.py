# encoding: utf-8

import functools
import inspect
import web.core

from paste.registry import StackedObjectProxy
from web.auth import middleware, predicates
from web.auth.predicates import *


__all__ = ['config', 'user', 'authenticate', 'deauthenticate', 'authorize'] + predicates.__all__
log = __import__('logging').getLogger(__name__)

config = None
user = StackedObjectProxy(name="user")

web.core.namespace['web']['auth'] = predicates
web.core.namespace['web']['user'] = user

def authenticate(identifier, password=None, force=False):
    """Authenticate a user.
    
    Sets the current user in the session.  You can optionally omit a password
    and force the authentication to authenticate as any user.
    
    If successful, the web.auth.user variable is immediately available.
    
    Returns True on success, False otherwise.
    """
    
    if force:
        result = (identifier, config.lookup(identifier))
    else:
        result = config.authenticate(identifier, password)
    
    if result is None or result[1] is None:
        log.debug('Authentication failed: %r', result)
        return False
    
    log.debug('Authentication successful: %r', result)
    
    web.core.session[config.name] = result[0]
    web.core.session.save()
    
    web.core.request.environ['paste.registry'].register(
            user,
            result[1]
        )
    
    return True


def deauthenticate(nuke=False):
    """Force logout.
    
    The web.auth.user variable is immediately deleted and session variable cleared.
    
    Additionally, this function can also completely erase the Beaker session.
    """
    
    if nuke:
        web.core.session.invalidate()
    
    web.core.session[config.name] = None
    web.core.session.save()
    
    web.core.request.environ['paste.registry'].register(user, None)


def authorize(predicate):
    """Decorator to enforce predicates.
    
    Evaluate predicates directly (using the bool callable) and raise a
    403 Forbidden error if you want to do this by hand.
    """
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            if not bool(predicate):
                raise web.core.http.HTTPForbidden()
            
            return func(*args, **kw)
        
        # Match wrapped function argspec.
        wrapper.__func_argspec__ = getattr(func, '__func_argspec__', inspect.getargspec(func))
        
        return wrapper
    
    return decorator
