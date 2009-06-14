# encoding: utf-8

"""
"""

import                                          sys, os
from webob                                      import Request, Response


__all__ = ['Application']
log = __import__('logging').getLogger(__name__)



class Application(object):
    """A WSGI-compliant application base.
    
    This implements the basics nessicary to function as a WSGI application.
    
    Additionally, if you need more than a simple WSGI application (which can
    be used with other WSGI components) and would like a full-stack
    environment, you can use the factory method to create a complete
    environment.
    """
    
    def __init__(self, root, **kw):
        self.root = root
        self.config = kw
    
    @classmethod
    def factory(cls, gconfig=dict(), root=None, **config):
        """Build a full-stack framework around this WSGI application."""
        
        log = __import__('logging').getLogger(__name__ + ':factory')
        log.info("Preparing YAPWF WSGI middleware stack.")
        
        from web.core import Controller
        from web.utils.object import get_dotted_object
        from paste.deploy.converters import asbool, asint
        
        root = config.get('web.root', root)
        log.debug("Root configured as %r.", root)
        
        # Find, build, and configure our basic Application instance.
        if isinstance(root, basestring):
            log.debug("Loading root controller from '%s'.", root)
            root = get_dotted_object(root)
        elif not issubclass(root, Controller):
            raise ValueError("The root controller must be defined using package dot-colon-notation or direct reference.")
        app = cls(root(), **config)
        
        # Automatically use Buffet templating engines unless explicitly forbidden.
        if asbool(config.get('web.buffet', True)):
            log.debug("Loading Buffet template engine middleware.")
            from web.core.middleware import TemplatingMiddleware
            app = TemplatingMiddleware(app, config)
        
        # Automatically use ToscaWidgets unless explicitly forbidden (or simply not found).
        if asbool(config.get('web.widgets', True)):
            try:
                from tw.api import make_middleware as ToscaWidgetsMiddleware
                
                log.debug("Loading ToscaWidgets middleware.")
                app = ToscaWidgetsMiddleware(app, config)
            
            except ImportError:
                log.warn("ToscaWidgets not installed, widget framework disabled.  You can remove this warning by explicitly defining widgets=False in your config.")
        
        # Determine if a database engine has been requested, and load the appropriate middleware.
        # TODO: YAPWF entry point for database engine middleware.
        if config.get('db.engine', None) == 'sqlalchemy':
            try:
                log.debug("Loading SQLAlchemy session middleware.")
                from web.db.sa import SQLAlchemyMiddleware
                
                model = get_dotted_object(config.get('db.model'))
                app = SQLAlchemyMiddleware(app, model, **config)
            
            except:
                log.exception("Unable to load requested database engine middleware, %s.", config.get('db.engine', None))
        
        
        from paste.config import ConfigMiddleware
        app = ConfigMiddleware(app, config)
        
        # Automatically use beaker-supplied services unless explicitly forbidden (or simply not found).
        if asbool(config.get('web.beaker', True)):
            try:
                from beaker.middleware import SessionMiddleware, CacheMiddleware
                
                beakerconfig = dict([(i[7:], j) for i, j in config.iteritems() if i.startswith('beaker.')])
                
                log.debug("Loading Beaker session and cache middleware.")
                app = SessionMiddleware(app, beakerconfig)
                app = CacheMiddleware(app, beakerconfig)
                
                del beakerconfig
            
            except ImportError:
                log.warn("Beaker not installed, sessions and caching disabled.  You can remove this warning by specifying beaker=False in your config.")
        
        try:
            if asbool(config.get('debug', False)):
                log.debug("Debugging enabled; exceptions raised will display an interactive traceback.")
                
                from weberror.evalexception import EvalException
                app = EvalException(app, gconfig)
            
            else:
                log.debug("Debugging disabled; exceptions raised will display a 500 error.")
                
                from weberror.errormiddleware import ErrorMiddleware
                app = ErrorMiddleware(app, gconfig)
        
        except ImportError:
            log.warn("WebError not installed, interactive exception handling and messaging disabled.")
        
        
        from paste.registry import RegistryManager
        app = RegistryManager(app)
        
        
        if asbool(config.get('web.profile', False)):
            log.debug("Enabling profiling support.")
            from paste.debug.profile import ProfileMiddleware
            app = ProfileMiddleware(app, log_filename=config.get('web.profile.file', 'profile.log.tmp'), limit=asint(config.get('web.profile.limit', 40)))
        
        # Enabled explicitly or while debugging so you can use Paste's HTTP server.
        if asbool(config.get('web.static', False)) or asbool(config.get('debug', False)):
            from paste.cascade import Cascade
            from paste.fileapp import DirectoryApp
            
            path = config.get('web.static.path', None)
            
            if path is None:
                # Attempt to discover the path automatically.
                path = __import__(root.__module__).__file__
                path = os.path.abspath(path)
                path = os.path.dirname(path)
                path = os.path.join(path, 'public')
            
            if not os.path.isdir(path):
                log.warn("Unable to find folder to serve static content from.  Please specify static.path in your config.")
            
            log.debug("Serving static files from '%s'.", path)
            
            app = Cascade([DirectoryApp(path), app], catch=[401, 403, 404])
        
        # Enable compression if requested.
        if asbool(config.get('web.compress', False)):
            log.debug("Enabling HTTP compression.")
            
            from paste.gzipper import middleware as GzipMiddleware
            app = GzipMiddleware(app, compress_level=asint(config.get('web.compress.level', 6)))
        
        log.info("YAPWF WSGI middleware stack ready.")
        
        return app
    
    def prepare(self, environment):
        import web.core
        
        if environment.has_key('paste.registry'):
            environment['paste.registry'].register(web.core.request, Request(environment))
            environment['paste.registry'].register(web.core.response, Response())
            
            if environment.has_key('beaker.cache'):
                environment['paste.registry'].register(web.core.cache, environment['beaker.cache'])
            
            if environment.has_key('beaker.session'):
                environment['paste.registry'].register(web.core.session, environment['beaker.session'])
    
    def __call__(self, environment, start_response):
        import web.core, web.utils
        
        try:
            self.prepare(environment)
            
            content = web.core.dispatch(self.root, web.core.request.path_info)
        
        except web.core.http.HTTPException, e:
            return e(environment, start_response)
        
        else:
            # TODO: Deal with unicode responses, file-like objects, and iterators.
            if not isinstance(content, basestring):
                return content
            
            if isinstance(content, unicode):
                web.core.response.unicode_body = content
            
            else:
                web.core.response.body = content
        
        return web.core.response(environment, start_response)
