# encoding: utf-8

from inspect import ismethod #, isclass
from itertools import chain
#from weakref import WeakKeyDictionary

from marrow.logging import Log, DEBUG
from marrow.logging.formats import LineFormat
from marrow.util.compat import native
from marrow.util.bunch import Bunch
from marrow.wsgi.exceptions import HTTPException

from web.core.tarjan import robust_topological_sort
from web.core.response import registry
from web.ext.base import BaseExtension


class ConfigurationException(Exception):
    pass


class MissingRequirement(ConfigurationException):
    pass


class Application(object):
    """The WebCore WSGI application."""
    
    __slots__ = ('_cache', 'Context', 'log', 'extensions', 'signals')
    
    SIGNALS = ('start', 'stop', 'prepare', 'dispatch', 'before', 'after', 'mutate', 'transform')
    
    def __init__(self, root, **config):
        # TODO: Check root via asserts.
        
        self._cache = dict()  # TODO: WeakKeyDictionary so we don't keep dynamic __lookup__ objects hanging around!
        
        config = self.prepare_configuration(config)
        self.Context = self.context_factory(root, config)
        
        self.log = self.Context.log.name('web.app')
        
        self.log.debug("Preparing extensions.")
        
        extensions = self.extensions = self.load_extensions(config)
        signals = self.signals = self.bind_signals(config, extensions)
        
        for ext in signals.start:
            ext(self.Context)
    
    def prepare_configuration(self, config):
        config = Bunch(config) if config else Bunch()
        
        # We really need this to be there later.
        if 'extensions' not in config:
            config.extensions = list()
        
        return config
    
    def context_factory(self, root, config):
        class Context(object):
            def __contains__(self, name):
                return hasattr(self, name)
            
            def __iter__(self):
                return ((i, getattr(self, i)) for i in dir(self) if i[0] != '_')
        
        Context.app = self
        Context.root = root
        Context.config = config
        
        sep = '\n' + ' ' * 37
        
        Context.log = Log(None, dict(
                    formatter=LineFormat("{now.ts}  {level.name:<7}  {name:<10}  {text}{data}", sep, sep)
                ), level=DEBUG).name('base')
        
        return Context
    
    def load_extensions(self, config):
        extensions = config.extensions  # we iterate this fairly frequently
        
        # If the base extension isn't present yet, add it.
        # TODO: Find all who are marked as always=True!
        if BaseExtension not in extensions:
            extensions.append(BaseExtension())
        
        # First let's check if everything needed has been provided.
        # We deal with 'uses' feature requirements later.
        
        provided = set().union(*(getattr(ext, 'provides', ()) for ext in extensions))
        needed = set().union(*(getattr(ext, 'needs', ()) for ext in extensions))
        
        if not provided.issuperset(needed):
            raise MissingRequirement("Extensions providing the following features must be configured:\n" +
                    ', '.join(needed.difference(provided)))
        
        # Now we spider the configured extensions and graph. This is a multi-step process.
        
        # Create a mapping of feature names to extensions. We only want extension objects in our initial graph.
        
        universal = list()  # these always go first (in any order)
        inverse = list()  # these always go last (in any order)
        provides = dict()
        
        for ext in extensions:
            for feature in getattr(ext, 'provides', ()):
                provides[feature] = ext
            
            if getattr(ext, 'first', False):
                universal.append(ext)
            elif getattr(ext, 'last', False):
                inverse.append(ext)
        
        # Now we build the initial graph.
        
        dependencies = dict()
        
        for ext in extensions:
            # We build a set of requirements from needs + uses that just happen to have been fulfilled.
            requirements = set(getattr(ext, 'needs', ()))
            requirements.update(set(getattr(ext, 'uses', ())).intersection(provided))
            
            dependencies[ext] = set(provides[req] for req in requirements)
            
            if universal and ext not in universal:
                dependencies[ext].update(universal)
            
            if inverse and ext in inverse:
                dependencies[ext].update(set(extensions).difference(inverse))
        
        # Build the final "unidirected acyclic graph"; a list of extensions in dependency-resolved order.
        dependencies = robust_topological_sort(dependencies)
        
        # If there are any tuple elements, we've got a circular reference!
        extensions = []
        for ext in dependencies:
            if len(ext) > 1:
                raise ConfigurationException("Circular dependency found: " + repr(ext))
            
            extensions.append(ext[0])
        
        return extensions
    
    def bind_signals(self, config, extensions):
        signals = Bunch((signal, []) for signal in self.SIGNALS)
        
        for ext in extensions:
            for mn in self.SIGNALS:
                m = getattr(ext, mn, None)
                if m:
                    signals[mn].append(m)
        
        signals.after.reverse()
        signals.mutate.reverse()
        signals.transform.reverse()
        
        return signals
    
    def __call__(self, environ, start_response=None):
        context = self.Context()
        context.environ = environ
        signals = self.signals
        
        for ext in chain(signals.prepare, signals.before):
            ext(context)
        
        exc = None
        
        self.log.debug("Starting dispatch.")
        
        # Terrible! Temporary! Hack! :D
        try:
            router = __import__('web.dialect.dispatch').dialect.dispatch.ObjectDispatchDialect(context.config)
            
            for consumed, handler, is_endpoint in router(context, context.root):
                for ext in signals.dispatch:
                    ext(context, consumed, handler, is_endpoint)
        except HTTPException as e:
            handler = e(context.request.environ)
        
        count = 0
        
        cache = self._cache
        
        try:
            # We need to determine if the returned object is callable.
            #  If not, continue.
            # Then if the callable is a bound instance method.
            #  If not call with the context as an argument.
            # Otherwise call.
            
            request = context.request
            
            if callable(handler):
                args = list(request.remainder)
                if args and args[0] == '': del args[0]
                kwargs = dict() # request.kwargs
                
                for ext in signals.mutate:
                    ext(context, handler, args, kwargs)
                
                if ismethod(handler) and getattr(handler, '__self__', None):
                    result = handler(*args, **kwargs)
                else:
                    result = handler(context, *args, **kwargs)
            else:
                result = handler
            
            for ext in signals.transform:
                ext(context, result)
            
            try:
                # We optimize for the general case whereby callables always return the same type of result.
                kind, renderer, count = cache[handler]
                
                # If the current return value isn't of the expceted type, invalidate the cache.
                # or, if the previous handler can't process the current result, invalidate the cache.
                if not isinstance(result, kind) or not renderer(context, result):
                    raise KeyError('Invalidating.')
                
                # Reset the cache miss counter.
                if count > 1:
                    cache[handler] = (kind, renderer, 1)
            
            except (TypeError, KeyError) as e:
                # Perform the expensive deep-search for a valid handler.
                renderer = registry(context, result)
                
                if not renderer:
                    raise Exception("Inappropriate return value or return value does not match response registry:\n\t" +
                            __import__('pprint').pformat(result))
                
                # If we're updating the cache excessively the optimization is worse than the problem.
                if count > 5:
                    renderer = registry
                
                # Update the cache if this isn't a TypeError.
                if not isinstance(e, TypeError):
                    cache[handler] = (type(result), renderer, count + 1)
        
        except Exception as exc:
            safe = isinstance(exc, HTTPException)
            
            if safe:
                context.response = exc
            
            for ext in signals.after:
                if ext(context, exc):
                    exc = None
            
            if exc and not safe:
                raise
        
        else:
            for ext in signals.after:
                ext(context, None)
        
        result = context.response(environ)
        
        if start_response:
            status, headers, body = result
            start_response(native(status), [(native(i), native(j)) for i, j in headers])
            return body
        
        return result
