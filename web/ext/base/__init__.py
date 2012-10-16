# encoding: utf-8

from marrow.wsgi.objects import Request, Response

from web.core.response import registry
from web.ext.base import handler
from web.ext.base.helpers import URLGenerator


class BaseExtension(object):
    first = True
    always = True
    provides = ["request", "response"]

    def __call__(self, context, app):
        context.log.name('web.app').debug("Preparing WSGI middleware stack.")
        return app

    def start(self, context):
        context.log.name('web.app').debug("Registering core return value handlers.")

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

        context.log.name('ext.base').debug("Preparing the request context.")

        context.request = Request(context.environ)
        context.response = Response(request=context.request)

        context.environ['web.base'] = context.request.path

        context.url = URLGenerator(context)
        context.path = []
        context.log = context.log.name('request').data(request=context.request)

    def dispatch(self, context, consumed, handler, is_endpoint):
        """Called as dispatch descends into a tier.

        The base extension uses this to maintain the "current url".
        """
        
        request = context.request
        context.log.name('ext.base').data(consumed=consumed, handler=handler, endpoint=is_endpoint).debug("Handling dispatch.")

        if len(consumed) != 1 or consumed[0]:
            request.path += consumed

        context.path.append((handler, request.path))
        request.remainder = request.remainder[len(consumed):]

        if not is_endpoint:
            context.environ['web.controller'] = str(context.request.path)
    
    # TODO: Move these logging messages to web.core.application and remove these superfluous callbacks.
    
    def stop(self, context):
        context.log.name('web.app').debug("Shutdown complete.")
    
    def graceful(self, context):
        context.log.name('web.app').debug("Performing graceful restart.")
    
    def before(self, context):
        context.log.name('web.app').debug("Preparing for dispatch.")

    def after(self, context, exc=None):
        context.log.name('web.app').data(exc=exc, response=context.response).debug("Registry processed, returning response.")

    def mutate(self, context, handler, args, kw):
        context.log.name('web.app').data(handler=handler, args=args, kw=kw).debug("Controller found, calling.")
    
    def transform(self, context, result):
        context.log.name('web.app').data(result=result).debug("Controller called, preparing for registry.")
