#!/usr/bin/env python2.5

import logging
from paste                                      import httpserver
from web.core                                   import Application, Controller, request, response


class RootController(Controller):
    def index(self):
        return 'Hello world!'
    
    def hello(self, name):
        return "Hello, %(name)s!" % dict(name=name)


application = Application.factory(root=RootController, debug=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    httpserver.serve(application, host='127.0.0.1', port='8080')
