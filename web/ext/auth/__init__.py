# encoding: utf-8

from functools import partial


class AuthenticationExtension(object):
    uses = ['template']
    needs = ['session']
    provides = ['auth', 'authentication', 'identity']
    
    def __init__(self, config):
        super(Extension, self).__init__()
    
    def prepare(self, context):
        """Prepare the variables from the context."""
        context.user = None
        context.acl = []
        context.namespace.user = context.user
        context.namespace.auth = predicates
        
        context.authenticate = partial(self.authenticate, context)
    
    def dispatch(self, context, consumed, handler, is_endpoint):
        acl = getattr(handler, '__acl__', [])
        context.acl.append(acl)
    
    def before(self, context):
        """Validate the ACL."""
        pass
    
    def authenticate(self, context, identifier, password=None, force=False):
        """Authenticate a user.
        
        Sets the current user in the session.  You can optionally omit a password
        and force the authentication to authenticate as any user.
        
        If successful, the web.auth.user variable is immediately available.
        
        Returns True on success, False otherwise.
        """
        
        if force:
            result = (identifier, self._lookup(identifier))
        else:
            result = self._authenticate(identifier, password)
        
        if result is None or result[1] is None:
            return False
        
        context.session[self._name] = result[0]
        context.session.save()
        
        context.user = result[1]
        
        return True
    
    def deauthenticate(self, context, nuke=False):
        """Force logout.
        
        The web.auth.user variable is immediately deleted and session variable cleared.
        
        Additionally, this function can also completely erase the Beaker session.
        """
        
        session = context.session
        
        if nuke:
            session.invalidate()
        
        session[self._name] = None
        
        if not session.autocommit:
            session.save()
        
        context.user = None


def authorize(predicate):
    """Decorator to enforce predicates.
    
    Evaluate predicates directly (using the bool callable) and raise a
    401 Not Authorized error if you want to do this by hand.
    """
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            if not bool(predicate):
                raise web.core.http.HTTPUnauthorized()
            
            return func(*args, **kw)
        
        # Match wrapped function argspec.
        wrapper.__func_argspec__ = getattr(func, '__func_argspec__', inspect.getargspec(func))
        
        return wrapper
    
    return decorator
