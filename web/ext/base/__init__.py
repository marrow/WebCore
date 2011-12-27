#.encoding: utf-8

from marrow.wsgi.objects import Request, Response

from web.core.response import registry
from web.ext.base import handler


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
        context.request = Request(context.environ)
        context.response = Response(request=context.request)
