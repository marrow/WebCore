# encoding: utf-8

from webob import Request, Response
import web.core


log = __import__('logging').getLogger(__name__)
__all__ = ['RESTMethod']



class RESTMethod(object):
    """Enable the writing of individual methods that map to REST verbs.
    
    Any HTTP method is allowed: GET PUT POST DELETE HEAD TRACE OPTIONS
    
    HEAD and OPTIONS are written for you, but can be overridden.
    
    With this it would possible to create a WebDAV system.
    """
    
    def __init__(self):
        super(RESTMethod, self).__init__()
        
        methods = []
        
        for i in ['get', 'put', 'post', 'delete', 'head', 'trace', 'options']:
            if hasattr(self, i) and hasattr(getattr(self, i), '__call__'):
                methods.append(i.upper())
        
        self.methods = methods
    
    def __call__(self, *args, **kw):
        if '_method' in kw:
            log.warning("Use of _method to override the HTTP verb is deprecated.  Use _verb instead.")
            kw['_verb'] = kw['_method']
        
        verb = kw.pop('_verb', web.core.request.method).lower()
        web.core.response.allow = self.methods
        
        log.debug("Performing REST dispatch to %s(%r, %r)", verb, args, kw)
        
        if verb.upper() not in self.methods:
            raise web.core.http.HTTPMethodNotAllowed()
        
        return getattr(self, verb)(*args, **kw)
    
    index = __call__
    __default__ = __call__
    
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
    
    def head(self, *args, **kw):
        """Allow the get method to set headers, but return no content.
        
        This performs an internal GET and strips the body from the response.
        """
        return self.get(*args, **kw)
    
    def options(self, *args, **kw):
        """The allowed methods are present in the returned headers."""
        
        return ''
