# encoding: utf-8

from marrow.wsgi.objects import Request, Response
from marrow.logging import Log, DEBUG

from web.core.response import registry
from web.ext.base import handler
from web.ext.base.helpers import URLGenerator


class BaseExtension(object):
    first = True
    always = True
    provides = ["request", "response"]
    
    def __init__(self, config):
        super(BaseExtension, self).__init__()
    
    def start(self):
        # Register the default return handlers.
        for h in handler.__all__:
            h = getattr(handler, h)
            registry.register(h, *h.types)
    
    def prepare(self, context):
        """Add the usual suspects to the context.
        
        The following are provided by the underlying application:
        
        * app -- the composed WSGI application
        * root -- the root controller object
        * config -- the complete configuration bunch
        * environ -- the current request environment
        """
        
        log = Log(level=DEBUG).name('request')  # TODO: Split this into the logging extension.
        
        log.debug("Preparing request context.")
        
        context.request = Request(context.environ)
        context.response = Response(request=context.request)
        
        context.environ['web.base'] = context.request.path
        
        context.url = URLGenerator(context)
        context.path = []
        context.log = log.data(request=context.request)
    
    def dispatch(self, context, consumed, handler, is_endpoint):
        """Called as dispatch descends into a tier.
        
        The base extension uses this to maintain the "current url".
        """
        context.log.data(consumed=consumed, handler=handler, endpoint=is_endpoint).debug("Handling dispatch.")
        
        context.request.path += consumed
        context.path.append((handler, context.request.path))
        
        for i in range(len(consumed)):
            context.request.remainder.pop()
        
        if not is_endpoint:
            context.environ['web.controller'] = str(context.request.path)
    
    def after(self, context, exc=None):
        pass
