# encoding: utf-8

from itertools import chain
from weakref import WeakKeyDictionary

from marrow.util.bunch import Bunch
from marrow.wsgi.exceptions import HTTPException, HTTPNotFound

from web.core.response import registry


class Application(object):
    """A WSGI2-compliant application base."""
    
    def __init__(self, root, config=None):
        config = Bunch(config) if config else Bunch()
        
        # TODO: Check root.
        
        self.root = root
        self.config = config
        
        # TODO: Graph the dependencies.
        # TODO: Generate the prepare/before/after sorted lists.
        
        self.extensions = []
        
        from web.ext.base import BaseExtension
        try:
            if 'base' in config and isinstance(config.base, dict):
                ec = Bunch(config.base)
            else:
                ec = Bunch.partial('base', config)
        except ValueError:
            ec = Bunch()
        self.extensions.append(BaseExtension(ec))
        
        from web.ext.template import TemplateExtension
        try:
            if 'template' in config and isinstance(config.template, dict):
                ec = Bunch(config.template)
            else:
                ec = Bunch.partial('template', config)
        except ValueError:
            ec = Bunch()
        self.extensions.append(TemplateExtension(ec))
        
        self._start = []
        self._stop = []
        self._prepare = []
        self._before = []
        self._after = []
        
        for ext in self.extensions:
            for mn in ('start', 'stop', 'prepare', 'before', 'after'):
                m = getattr(ext, mn, None)
                if not m: continue
                getattr(self, '_' + mn).append(m)
        
        for ext in self._start:
            ext()
        
        self._cache = WeakKeyDictionary()
    
    def __call__(self, environ):
        context = Bunch()
        
        context.app = self
        context.root = self.root
        context.config = self.config
        context.environ = environ
        
        for ext in chain(self._prepare, self._before):
            ext(context)
        
        exc = None
        
        # TODO: Dispatch.
        callable = self.root
        count = 0
        
        try:
            result = callable(context)
            
            try:
                # We optimize for the general case whereby callables always return the same type of result.
                kind, handler, count = self._cache[callable]
                
                # If the current return value isn't of the expceted type, invalidate the cache.
                # or, if the previous handler can't process the current result, invalidate the cache.
                if not isinstance(result, kind) or not handler(context, result):
                    raise KeyError('Invalidating.')
                
                # Reset the cache miss counter.
                if count > 1:
                    self._cache[callable] = (kind, handler, 1)
            
            except KeyError:
                # Perform the expensive deep-search for a valid handler.
                handler = registry(context, result)
                
                if not handler:
                    raise Exception("Inappropriate return value or return value does not match response registry:\n\t" +
                            __import__('pprint').pformat(result))
                
                # If we're updating the cache excessively the optimization is worse than the problem.
                if count > 5:
                    handler = registry
                
                # Update the cache.
                self._cache[callable] = (type(result), handler, count + 1)
        
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
        
        return result


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # enhanced wsgi2 application
    def enhanced(context):
        return b'200 OK', [(b'Content-Type', b'text/plain'), (b'Content-Length', b'12')], [b'Hello world.']
    
    # one-function WebCore 2 application
    def basic(context):
        context.response.mime = b'text/plain'
        return "Hello world."
    
    # template-based one-function WebCore 2 application
    def template(context):
        return 'mako:./test.html', dict()
    
    # test of exception handling
    def exception(context):
        raise HTTPNotFound()
    
    app = Application(template)
    
    from marrow.server.http import HTTPServer
    HTTPServer('127.0.0.1', 8080, application=app).start()
