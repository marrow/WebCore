# encoding: utf-8

import web.core
import webob.exc
from paste.registry import StackedObjectProxy

import middleware

from predicates import *


__all__ = ['config', 'user', 'authenticate', 'deauthenticate', 'authorize'] + predicates.__all__
log = __import__('logging').getLogger(__name__)

config = None
user = StackedObjectProxy(name="user")

web.core.namespace['web'].auth = predicates
web.core.namespace['web'].user = user


def authenticate(identifier, password=None, force=False):
    """Authenticate a user.
    
    Sets the current user in the session.  You can optionally omit a password
    and force the authentication to authenticate as any user.
    
    If successful, the web.auth.user variable is immediately available.
    
    Returns True on success, False otherwise.
    """
    
    try:
        result = config.authenticate(identifier, password, force)
    
    except:
        result = (identifier, config.lookup(identifier))
        
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
    401 Not Authorized error if you want to do this by hand.
    """
    
    def decorator(func):
        def wrapper(*args, **kw):
            if not bool(predicate):
                raise webob.exc.HTTPUnauthorized()
            
            return func(*args, **kw)
        
        # Become more transparent.
        if hasattr(func, '__name__'):
            wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__dict__ = func.__dict__
        wrapper.__module__ = func.__module__
        
        return wrapper
    
    return decorator
