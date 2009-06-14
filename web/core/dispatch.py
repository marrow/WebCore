# encoding: utf-8

"""
Object dispatch mechanism engineered from the TurboGears 2 documentation.

This allows you to define a class heirarchy using a simple declarative
style. Additionally, this gives you access to powerful dynamic dispatch
using the `default` and `lookup` fallback mechanisms.

Example:

    class RootController(Controller):
        def index(self):
            return "Hello world!"
    
    web.config.root = RootController()
"""


log = __import__('logging').getLogger(__name__)
__all__ = ['Application', 'env']



class Controller(object):
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
        """The __afteR__ method can modify the value returned by the final method call."""
        return result


def dispatch(root, path):
    # TODO: Allow method-specific hooks through decoration.
    
    from web.core import http, request, config
    
    parts = path.strip('/').split('/') if path.strip('/') else []
    location = root
    data = request.params.mixed()
    parent = None
    
    request.script_name = ''
    
    #request['SCRIPT_NAME'] += '/' + next
    #request['PATH_INFO'] = rest
    
    log.debug("Dispatching %r - %r %r %r", path, parts, location, data)
    
    while True:
        if not parts:
            # If the final object under consideration is a controller, not a method, attempt to call the index method, then attempt the default method, or bail with a 404.
            if not path.endswith('/') and config.get('trailing_slashes', True):
                location = path + '/'
                if request.environ.get('QUERY_STRING'):
                    location += '?' + request.environ.get('QUERY_STRING')
                raise http.HTTPMovedPermanently(location=location)
            
            log.debug("No parts, looking for index.")
            parts.append('index')
        
        part = parts.pop(0)
        parent = location
        location = getattr(location, part, None)
        
        log.debug("Dispatching part %r in %r, found %r.", part, parent, location)
        
        # If the current object under consideration is a decorated controller method, the search is ended.
        if callable(location) and not part.startswith('_'):
            log.debug("Location %r is callable.", location)
            
            request.script_name += '/' + part
            request.path_info = '/'.join(parts)
            
            parts, data = parent.__before__(*parts, **data)
            result = location(*parts, **data)
            return parent.__after__(result, *parts, **data)
        
        # If the URL portion exists as an attribute on the object in question, start searching again on that attribute.
        if isinstance(location, Controller) and not part.startswith('_'):
            log.debug("Location %r is a class, continuing search.", location)
            request.environ['SCRIPT_NAME'] += '/' + part
            continue
        
        # If the current object under consideration has a “default” method then the search is ended with that method returned.
        if callable(getattr(parent, 'default', None)):
            log.debug("Calling default method of %r for %r.", parent, [part] + parts)
            
            request.script_name += '/default'
            request.path_info = '/'.join([part] + parts)
            
            parts, data = parent.__before__(*([part] + parts),**data)
            result = parent.default(*parts, **data)
            return parent.__after__(result, *parts, **data)
        
        # If the current object under consideration has a “lookup” method then execute the “lookup” method, and start the search again on the return value of that method.
        if callable(getattr(parent, 'lookup', None)):
            log.debug("Calling lookup method of %r for %r.", parent, [part] + parts)
            
            # TODO: This should be checked... SCRIPT_NAME goes out the window a bit with redirected lookups...
            request.environ['SCRIPT_NAME'] += '/' + part
            
            location, parts = parent.lookup(*([part] + parts), **data)
            parts = list(parts)
            continue
        
        raise http.HTTPNotFound()
