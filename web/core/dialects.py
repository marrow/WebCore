# encoding: utf-8

import web.core


log = __import__('logging').getLogger(__name__)
__all__ = ['Application', 'env']



class Dialect(object):
    """A basic method of dispatching requests from WSGI.
    
    Subclasses allow for extreme levels of control over how content is found
    and returned to the end user.
    
    Examples include the basic object-dispatch Controller, the Routes-based
    RoutingController for improved performance, XMLRPCController, or
    AMFController for Flash/Flex integration.
    
    These are called dialects due to the fact that XML-RPC and AMF, and
    potentially future protocols, are fundamentally different to standard
    HTTP file-based operation, despite operating over HTTP.
    """
    
    def __call__(self, request):
        """Controller base classes implement this.
        
        This takes no arguments (all input should be processed from the request object)
        and should return content to the higher level processing middleware.
        """
        raise NotImplementedError



class Controller(Dialect):
    """Object dispatch mechanism engineered from the TurboGears 2 documentation.

    This allows you to define a class heirarchy using a simple declarative
    style. Additionally, this gives you access to powerful dynamic dispatch
    using the `default` and `lookup` fallback mechanisms.

    Example:

        class RootController(Controller):
            def index(self):
                return "Hello world!"

        web.config.root = RootController()
    
    This will likely be the most often used dialect as it offers the fastest prototyping
    and reasonable performance.
    
    For improved performance, consider using a RoutingController.
    """
    
    def __call__(self, request):
        """Non-recursively descend through Controller instances.
        
        If we encounter a non-Controller Dialect instance, pass on the modified request.
        """
        
        last = None
        part = self
        
        while True:
            last = part
            part = request.path_info_peek()
            
            if not part:
                # If the last object under consideration was a controller, not a method,
                # attempt to call the index method, then attempt the default, or bail
                # with a 404 error.
                
                if not request.path.endswith('/') and getattr(last, '__trailing_slash__', web.core.config.get('trailing_slashes', True)):
                    location = request.path + '/' + (('?' + request.query_string) if request.query_string else '')
                    log.debug("Trailing slash omitted from path, redirecting to %s.", location)
                    raise web.core.http.HTTPMovedPermanently(location=location)
                
                log.debug("No method given, searching for index method.")
                part = 'index'
            
            log.debug("Looking for %r attribute of %r.", part, last)
            protected, part = part.startswith('_'), getattr(last, part, None)
            data = request.params.mixed()
            remaining = request.path_info.strip('/')
            remaining = remaining.split('/') if remaining else []
            
            if not protected:
                if not isinstance(part, Controller) and isinstance(part, Dialect):
                    log.debug("Context switching from Controller to other Dialect instance.")
                    request.path_info_pop()
                    return part(request)
                
                # If the URL portion exists as an attribute on the object in question, start searching again on that attribute.
                if isinstance(part, Controller):
                    log.debug("Continuing descent through controller structure.")
                    request.path_info_pop()
                    continue
                
                # If the current object under consideration is a decorated controller method, the search is ended.
                if callable(part):
                    log.debug("Found callable, passing control. part(%r, %r)", remaining[1:], data)
                    request.path_info_pop()
                    remaining, data = last.__before__(*remaining[1:], **data)
                    return last.__after__(part(*remaining, **data))
            
            fallback = None
            
            try: fallback = last.default
            except AttributeError: pass
            
            if fallback:
                # If the current object under consideration has a “default” method then the search is ended with that method returned.
                log.debug("Calling default method of %r.", last)
                remaining, data = last.__before__(*remaining, **data)
                return last.__after__(fallback(*remaining, **data))
            
            try: fallback = last.lookup
            except AttributeError: pass
            
            if fallback:
                # If the current object under consideration has a “lookup” method then execute the “lookup” method, and start the search again on the return value of that method.
                log.debug("Calling lookup method of %r.", last)
                try:
                    part, remaining = fallback(*remaining, **data)
                    request.path_info = '/' + '/'.join(remaining) + ('/' if request.path.endswith('/') else '')
                    continue
                except:
                    log.exception("Error calling lookup method.")
                    raise
            
            raise web.core.http.HTTPNotFound()
    
    def __before__(self, *args, **kw):
        """The __before__ method can modify arguments passed in to the final method call.
        
        To subclass and overload this method, ensure you use the following form:
        
        class Foo(Controller):
            def __before__(self, *args, **kw):
                # Perform your actions here...
                # Finally, allow superclasses to modify the arguments as well...
                return super(Foo, self).__before__(*args, **kw)
        """
        return args, kw
    
    def __after__(self, result, *args, **kw):
        """The __after__ method can modify the value returned by the final method call."""
        return result
