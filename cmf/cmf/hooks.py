# encoding: utf-8

"""

System-wide hook mechanism.

"""


log = __import__('logging').getLogger(__name__)
__all__ = ['GlobalHooks', 'authorize']


class GlobalHooks(object):
    """ Simple class to support 'simple registration' type decorators
    
    The decoration object can be 
    
    """
    def __init__(self):
        self.engines = {}
        self.validation = None
        self.error_handler = None
        self.hooks = dict(
                authorized = []
            )
    
    def __getattr__(self, name):
        return self.hooks[name]
    
    def register_hook(self, name, func):
        """Registers the specified function as a hook."""
        self.hooks[name].append(func)


hooks = GlobalHooks()


class _hook_decorator(object):
    """SuperClass for all hooks."""
    
    hook_name = None    # must be overridden by a particular hook
    
    def __init__(self, hook_func):
        log.debug("Hook Decorator __init__: %r", hook_func)
        self.hook_func = hook_func
        hooks.register_hook(self.hook_name, hook_func)
    
    def __call__(self, *args, **kw):
        log.debug("Hook Decorator __call__(%r) (%r, %r)", self.hook_func, args, kw)
        return self.hook_func


class authorize(_hook_decorator):
    """Callable to be queried to pass/grant/deny access to an asset.
    
    If the callable returns None it does not impact authorization.
    If it returns True, validation is immediately stopped and access granted.
    If all callables in the hook list return False, access is denied.
    """
    hook_name = 'authorized'

