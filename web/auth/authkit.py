# encoding: utf-8

"""WebCore-specific AuthKit adaptors."""

from decorator import decorator
from web.core import config, request

from authkit.authorize import PermissionSetupError
from authkit.authorize import NotAuthenticatedError, NotAuthorizedError
from authkit.authorize import authorize_request as authkit_authorize_request


__all__ = ['authorize', 'authorize_request', 'authorized']



def authorize(permission):
    """
    This is a decorator which can be used to decorate a controller action.
    It takes the permission to check as the only argument and can be used with
    all types of permission objects.
    """
    
    def validate(func, self, *args, **kwargs):
        if request.environ.get('paste.config', dict()).get('web.auth', 'false').lower() not in ('true', 'yes', 'on', 'authkit'):
            raise Exception('AuthKit not enabled.  Enable \'web.auth\' in your INI file.')
            
        def app(environ, start_response):
            return func(self, *args, **kwargs)
        
        return permission.check(app, request.environ, None)
    
    return decorator(validate)


def authorize_request(permission):
    """
    This function can be used within a controller action to ensure that no code 
    after the function call is executed if the user doesn't pass the permission
    check specified by ``permission``.
    """
    authkit_authorize_request(request.environ, permission)

def authorized(permission):
    """
    Similar to the ``authorize_request()`` function with no access to the
    request but rather than raising an exception to stop the request if a
    permission check fails, this function simply returns ``False`` so that you
    can test permissions in your code without triggering a sign in. It can
    therefore be used in a controller action or template.

    Use like this::

        if authorized(permission):
            return 'You are authorized'
        else:
            return 'Access denied'
 
    """
    try:
        authorize_request(permission)
    except (NotAuthorizedError, NotAuthenticatedError):
        return False
    else:
        return True

