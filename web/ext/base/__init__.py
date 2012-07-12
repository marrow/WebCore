# encoding: utf-8

from marrow.wsgi.objects import Request, Response
from marrow.logging import Log, DEBUG
from marrow.logging.formats import LineFormat

from web.core.response import registry
from web.ext.base import handler
from web.ext.base.helpers import URLGenerator


class BaseExtension(object):
    first = True
    always = True
    provides = ["request", "response"]

    def __init__(self, config):
        super(BaseExtension, self).__init__()
        self.log = Log(None, dict(
                formatter=LineFormat("{now.ts}  {level.name:>5}  {name:<10}  {data}  {text}", '  ')
            ), level=DEBUG).name('base')
        
        self.log.debug("Configuring the base extension.")

    def __call__(self, app):
        self.log.debug("Preparing WSGI middleware stack.")
        return app

    def start(self):
        self.log.name('start').debug("Starting up.")

        # Register the default return handlers.
        for h in handler.__all__:
            h = getattr(handler, h)
            registry.register(h, *h.types)

    def stop(self):
        self.log.debug("Shutdown complete.")

    def graceful(self):
        self.log.debug("Performing graceful restart.")

    def prepare(self, context):
        """Add the usual suspects to the context.

        The following are provided by the underlying application:

        * app -- the composed WSGI application
        * root -- the root controller object
        * config -- the complete configuration bunch
        * environ -- the current request environment
        """

        self.log.name('prepare').debug("Preparing the request context.")

        log = self.log.name('request')  # TODO: Split this into the logging extension.

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

        self.log.name('dispatch').data(consumed=consumed, handler=handler, is_endpoint=is_endpoint).debug("Dispatch received.")

        request = context.request

        context.log.data(consumed=consumed, handler=handler, endpoint=is_endpoint).debug("Handling dispatch.")

        if len(consumed) != 1 or consumed[0]:
            request.path += consumed

        context.path.append((handler, request.path))
        request.remainder = request.remainder[len(consumed):]

        if not is_endpoint:
            context.environ['web.controller'] = str(context.request.path)

    def before(self, context):
        self.log.name('before').debug("Preparing for dispatch.")

    def after(self, context, exc=None):
        self.log.name('after').data(exc=exc).debug("Registry processed, returning response.")

    def mutate(self, context, handler, args, kw):
        self.log.name('mutate').data(handler=handler, args=args, kw=kw).debug("Controller found, calling.")
    
    def transform(self, context, result):
        self.log.name('transform').data(result=result).debug("Controller called, preparing for registry.")


