# encoding: utf-8

from marrow.wsgi.exceptions import HTTPMethodNotAllowed


class ResourceDialect(object):
    def __init__(self, config):
        pass
    
    def __call__(self, context, root):
        action = context.request.method.lower()
        method = getattr(root, action, None)
        
        if not method and action in ('head', 'options'):
            method = getattr(self, action)
        
        if not method:
            raise HTTPMethodNotAllowed()
        
        yield '', method, True
    
    def head(self, *args, **kw):
        """Allow the get method to set headers, but return no content.
        
        This performs an internal GET and strips the body from the response.
        """
        return self.get(*args, **kw)
    
    def options(self, *args, **kw):
        """The allowed methods are present in the returned headers."""
        
        return ''
