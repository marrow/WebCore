# encoding: utf-8

"""

"""

import threading

from web.core.dispatch import Controller
from web.core.application import Application
from web.utils.dictionary import adict
from webob import exc as http
from web.core.dispatch import dispatch

__all__ = ['Application', 'config', 'request', 'response', 'http', 'dispatch']


config = adict(
        response=adict(content_type='text/html', charset='utf8')
    )

ctx = threading.local()



if __name__ == '__main__':
    import logging
    from paste import httpserver
    # from weberror.errormiddleware import ErrorMiddleware
    
    logging.basicConfig(level=logging.INFO)
    
    class RootController(Controller):
        def index(self):
            return 'Hello world!'
        
        def hello(self, name):
            return "Hello, %(name)s!" % dict(name=name)
    
    root = RootController()
    app = Application(root)
    # app = ErrorMiddleware(app, debug=True)
    
    httpserver.serve(app, host='127.0.0.1', port='8080')