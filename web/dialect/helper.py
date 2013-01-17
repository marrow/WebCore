# encoding: utf-8

"""Helpers for advanced controller behaviour.

Much work needs to be done.
"""

from functools import partial, wraps

from marrow.wsgi.exceptions import HTTPMethodNotAllowed


class Method(object):
    _allowable = ('get', 'put', 'post', 'delete', 'head', 'trace', 'options')
    
    def __init__(self, real=True):
        self._methods = ['OPTIONS']
        self._real = real
    
    def _handler(self, method, obj):
        instance = self
        
        if not self._real:
            instance = self.__class__(True)
        
        setattr(instance, method, obj)
        instance._methods.append(method.upper())
        
        if method == 'get':
            instance._methods.append('HEAD')
        
        return instance
    
    def __getattr__(self, name):
        if name not in self._allowable:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))
        
        return partial(self._handler, name)
    
    def __call__(self, context):
        request = context.request
        verb = request.kwargs.pop('_verb', request.method).lower()
        request.method = verb.upper()
        context.response.allow = self._methods
        
        if request.method not in self._methods:
            raise HTTPMethodNotAllowed()
        
        return getattr(self, verb)(*request.remainder, **request.kwargs)
    
    def head(self, *args, **kw):
        """Allow the get method to set headers, but return no content.
        
        This performs an internal GET and strips the body from the response.
        """
        return self.get(*args, **kw)
    
    def options(self, *args, **kw):
        """The allowed methods are present in the returned headers."""
        return ''

method = Method(False)


def render(template, format=None):
    def decorator(fn):
        setattr(fn, '_needs_context', True)
        
        wrap = False
        
        if not hasattr(fn, '_template'):
            setattr(fn, '_template', dict())
            wrap = True
        
        fn._template[format or (template[:-1] if template[-1] == ':' else None)] = template
        
        if wrap:
            @wraps(fn)
            def inner(self, ctx, *args, **kw):
                result = fn(self, *args, **kw)
                
                if isinstance(result, (dict, list)):
                    return fn._template[ctx.request.format], result
                
                return result
            
            return inner
        
        return fn
    
    return decorator


def condition(*predicates):
    def decorator(fn):
        if hasattr(fn, '_conditions'):
            fn._conditions.append()
        
        fn.condition()
        
        @wraps(fn)
        def inner(self, ctx, *args, **kw):
            # Evaluate conditionals in turn.
            return fn(self, *args, **kw)
        
        return inner
    
    return decorator
