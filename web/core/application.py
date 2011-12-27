# encoding: utf-8

from itertools import chain

from marrow.util.bunch import Bunch

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
    
    def __call__(self, environ):
        context = Bunch()
        
        context.root = self.root
        context.config = self.config
        context.environ = environ
        
        for ext in chain(self._prepare, self._before):
            ext(context)
        
        exc = None
        
        try:
            result = self.root(context)
            handler = registry(context, result)
            
            if not handler:
                raise Exception("Inappropriate return value or return value does not match response registry:\n\t" +
                        __import__('pprint').pformat(result))
            
            self.root._handler = handler
        
        except Exception as exc:
            raise
        
        for ext in self._after:
            ext(context, exc)
        
        result = context.response()
        
        # __import__('pdb').set_trace()
        
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
    
    app = Application(basic)
    
    from marrow.server.http import HTTPServer
    HTTPServer('127.0.0.1', 8080, application=app).start()
