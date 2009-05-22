# encoding: utf-8

"""
"""

from webob import Request, Response


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
    
    def __init__(self, root):
        self.root = root
    
    @classmethod
    def factory(cls, gconfig=dict(), root=None, complete=True, **config):
        """Build a full-stack framework around this WSGI application."""
        
        from paste.deploy.converters import asbool
        
        from beaker.middleware import SessionMiddleware, CacheMiddleware
        from paste.cascade import Cascade
        from paste.registry import RegistryManager
        from paste.gzipper import make_gzip_middleware
        from paste.debug.profile import ProfileMiddleware
        from weberror.errormiddleware import ErrorMiddleware
        
        from web.utils.object import get_dotted_object
        
        # Find, build, and configure our basic Application instance.
        if isinstance(root, basestring):
            root = get_dotted_object(root)
        app = cls(root())
        
        # Beaker-supplied services.
        app = SessionMiddleware(app, config)
        app = CacheMiddleware(app, config)
        
        # app = recursive.RecursiveMiddleware(app, config)
        
        if asbool(complete):
            # Handle Python exceptions.
            app = ErrorMiddleware(app, gconfig, **config.get('errorhandler', dict(debug=config.get('debug', False))))
            
            # ErrorHandler not ErrorMiddleware
            # Display error documents for 401, 403, 404 status codes (and 500 when debug is disabled).
            # FROM: pylons
            #if asbool(config.get('debug', False)):
            #    app = StatusCodeRedirect(app)
            #else:
            #    app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])
        
        # TODO: Handle static files.
        
        app = RegistryManager(app)
        
        return app
        
    
    def prepare(self, environment):
        
        log.debug("Preparing environment: %r", environment)
        
        import web.core
        
        request = Request(environment)
        response = Response() # **web.core.config.response
        
        if environment.has_key('paste.registry'):
            environment['paste.registry'].register(web.core.request, request)
            environment['paste.registry'].register(web.core.response, response)
        
        log.debug("Environment prepared: %r %r", web.core.request, web.core.response)
    
    def __call__(self, environment, start_response):
        import web.core, web.utils
        
        try:
            self.prepare(environment)
            
            content = web.core.dispatch(self.root, web.core.request.path_info)
        
        except web.core.http.HTTPException, e:
            return e(environment, start_response)
        
        else:
            # TODO: Deal with unicode responses, file-like objects, and iterators.
            web.core.response.body = content
        
        return web.core.response(environment, start_response)
