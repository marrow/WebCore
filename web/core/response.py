# encoding: utf-8

log = __import__('logging').getLogger(__name__)


class ResponseRegistry(object):
    __slots__ = ('registry', )
    
    def __init__(self):
        self.registry = list()
    
    def register(self, handler, *types):
        self.registry.insert(0, (types, handler))
    
    def __call__(self, context, response):
        for k, v in self.registry:
            if isinstance(response, k):
                if v(context, response):
                    return v
        return False


registry = ResponseRegistry()
