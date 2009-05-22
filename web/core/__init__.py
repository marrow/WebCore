# encoding: utf-8

"""

"""

from web.core.dispatch import Controller
from web.core.application import Application
from web.utils.dictionary import adict
from webob import exc as http
from web.core.dispatch import dispatch

from paste.registry import RegistryManager, StackedObjectProxy


__all__ = ['Controller', 'Application', 'config', 'ctx', 'http', 'dispatch']


config = adict(
        response=adict(content_type='text/html', charset='utf8')
    )

request = StackedObjectProxy()
response = StackedObjectProxy()



if __name__ == '__main__':
    import logging
    from paste import httpserver
    
    logging.basicConfig(level=logging.INFO)
    
    class RootController(Controller):
        def index(self):
            return 'Hello world!'
        
        def hello(self, name):
            return "Hello, %(name)s!" % dict(name=name)
        
        def env(self, *args, **kw):
            ctx.response.content_type = "text/plain"
            return "Request:\n%s" % ( "\n".join(["%s: %r" % (i,j) for i,j in ctx.request]), )
    
    app = Application.factory(root=RootController, debug=True)
    
    httpserver.serve(app, host='127.0.0.1', port='8080')