# encoding: utf-8

from inspect import ismethod
from itertools import chain
from weakref import WeakKeyDictionary

from marrow.logging import Log, DEBUG
from marrow.logging.formats import LineFormat
from marrow.util.bunch import Bunch
from marrow.util.object import load_object
from marrow.wsgi.exceptions import HTTPException, HTTPNotFound

from web.core.response import registry


class Application(object):
    """A WSGI2-compliant application base."""
    
    def __init__(self, root, config=None):
        config = Bunch(config) if config else Bunch()
        
        # TODO: Check root via asserts.
        
        class Context(object):
            def __contains__(self, name):
                return hasattr(self, name)
            
            def __iter__(self):
                return ((i, getattr(self, i)) for i in dir(self) if i[0] != '_')
        
        Context.app = self
        Context.root = root
        Context.config = config
        
        Context.log = Log(None, dict(
                    formatter=LineFormat("{now.ts}  {level.name:<7}  {name:<10}  {data}  {text}", '  ', ' ' * 40)
                ), level=DEBUG).name('base')
        
        self.Context = Context
        
        self.extensions = []
        
        # TODO: Self-organizing extension selection.
        def load_extension(name, reference):
            ext = load_object(reference)
            extconfig = config.get('extensions', dict()).get(name, dict())
            
            self.extensions.append(ext(self.Context, **extconfig))
        
        load_extension('base', 'web.ext.base:BaseExtension')
        load_extension('cast', 'web.ext.cast:CastExtension')
        load_extension('template', 'web.ext.template:TemplateExtension')
        # ODOT
        
        # TODO: Make this a little more flexible.
        self._start = []
        self._stop = []
        self._prepare = []
        self._dispatch = []
        self._before = []
        self._after = []
        self._mutate = []
        self._transform = []
        
        for ext in self.extensions:
            for mn in ('start', 'stop', 'prepare', 'dispatch', 'before', 'after', 'mutate', 'transform'):
                m = getattr(ext, mn, None)
                if not m: continue
                getattr(self, '_' + mn).append(m)
        
        self._after.reverse()
        self._mutate.reverse()
        self._transform.reverse()
        # ODOT
        
        for ext in self._start:
            ext(self.Context)
        
        self._cache = dict() # TODO: WeakKeyDictionary so we don't keep dynamic __lookup__ objects hanging around!
    
    def __call__(self, environ, start_response=None):
        context = self.Context()
        context.environ = environ
        
        for ext in chain(self._prepare, self._before):
            ext(context)
        
        exc = None
        
        context.log.debug("Starting dispatch.")
        
        # Terrible! Temporary! Hack! :D
        try:
            router = __import__('web.dialect.dispatch').dialect.dispatch.ObjectDispatchDialect(context.config)
            
            for consumed, handler, is_endpoint in router(context, context.root):
                for ext in self._dispatch:
                    ext(context, consumed, handler, is_endpoint)
        except HTTPException as e:
            handler = e(context.request.environ)
        
        count = 0
        
        try:
            # We need to determine if the returned object is callable.
            #  If not, continue.
            # Then if the callable is a bound instance method.
            #  If not call with the context as an argument.
            # Otherwise call.
            
            request = context.request
            
            if callable(handler):
                args = list(request.remainder)
                if args[0] == '': del args[0]
                kwargs = request.kwargs
                
                for ext in self._mutate:
                    ext(context, handler, args, kwargs)
                
                if ismethod(handler) and getattr(handler, '__self__', None):
                    result = handler(*args, **kwargs)
                else:
                    result = handler(context, *args, **kwargs)
            else:
                result = handler
            
            for ext in self._transform:
                ext(context, result)
            
            try:
                # We optimize for the general case whereby callables always return the same type of result.
                kind, renderer, count = self._cache[handler]
                
                # If the current return value isn't of the expceted type, invalidate the cache.
                # or, if the previous handler can't process the current result, invalidate the cache.
                if not isinstance(result, kind) or not renderer(context, result):
                    raise KeyError('Invalidating.')
                
                # Reset the cache miss counter.
                if count > 1:
                    self._cache[handler] = (kind, renderer, 1)
            
            except (TypeError, KeyError):
                # Perform the expensive deep-search for a valid handler.
                renderer = registry(context, result)
                
                if not renderer:
                    raise Exception("Inappropriate return value or return value does not match response registry:\n\t" +
                            __import__('pprint').pformat(result))
                
                # If we're updating the cache excessively the optimization is worse than the problem.
                if count > 5:
                    renderer = registry
                
                # Update the cache.
                try:
                    self._cache[handler] = (type(result), renderer, count + 1)
                except TypeError:
                    pass
        
        except HTTPException as exc:
            context.response = exc
        
        except Exception as exc:
            for ext in self._after:
                if ext(context, exc):
                    exc = None
            
            if exc:
                raise
        
        else:
            for ext in self._after:
                ext(context, None)
        
        result = context.response(environ)
        
        if start_response:
            start_response(*result[:2])
            return result[3]
        
        return result
