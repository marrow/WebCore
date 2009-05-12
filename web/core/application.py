# encoding: utf-8

"""
"""

from webob import Request, Response


__all__ = ['Application']
log = __import__('logging').getLogger(__name__)



class Application(object):
    """A WSGI-compliant application base.
    
    This implements the basics nessicary to function as a WSGI application."""
    
    def __init__(self, root):
        self.root = root
    
    def prepare(self, environment):
        
        log.debug("Preparing environment: %r", environment)
        
        import web.core
        
        log.debug("Preparing request...")
        request = Request(environment)
        log.debug("Preparing request... [local]")
        web.core.ctx.request = request
        log.debug("Preparing request... done.")
        
        log.debug("Preparing response...")
        response = Response() # **web.core.config.response
        log.debug("Preparing response... [local]")
        web.core.ctx.response = response
        log.debug("Preparing response... done.")
        
        log.debug("Environment prepared: %r %r", web.core.ctx.request, web.core.ctx.response)
    
    def __call__(self, environment, start_response):
        import web.core, web.utils
        
        self.prepare(environment)
        
        try:
            content = web.core.dispatch(self.root, web.core.ctx.request.path_info)
        
        except web.core.http.HTTPException, e:
            return e(environment, start_response)
        
        else:
            # TODO: Deal with unicode responses, file-like objects, and iterators.
            web.core.ctx.response.body = content
        
        return web.core.ctx.response(environment, start_response)

