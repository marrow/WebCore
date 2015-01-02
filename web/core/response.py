# encoding: utf-8

"""Respone / view registry.

WebCore uses a return type (or response) registry to transform values returned by controllers for use as a responese.
This translation process is used to support the built-in types (see the `base` extension) and can be extended by your
own application to support additional types.  This is effectively the "view" component of Model-View-Controller.

The `template` extension provides support for template-based views using this mechanism.

## Automatic Transformation of Models

If you frequently hand back serialized data, you may be able to simplify your controller code and reduce boilerplate
by simply returning your model instances.  By registering a response handler for your model class you can implement
the serialization in a single, centralized location, making security and testing much easier.

## Exception Processing

When a controller raises an HTTPError subclass it is treated as the return value.  As such you can take specific
action on any given error, including rendering a pretty error page, etc.  By default these exceptions are treated as
a WSGI application and are executed, but only if no more specific handlers are registered.

Certain extensions, such as the debugging extension, provide their own exception handlers.

"""


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
