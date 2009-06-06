#!/usr/bin/env python2.5
# encoding: utf-8

from web.core                           import Application, Controller


class RootController(Controller):
    def index(self):
        return 'Hello world!'

    def hello(self, name):
        return "Hello, %(name)s!" % dict(name=name)


app = Application.factory(root=RootController, debug=False)

if __name__ == '__main__':
    import                                  logging
    from paste                              import httpserver
    
    logging.basicConfig(level=logging.INFO)
    httpserver.serve(app, host='127.0.0.1', port='8080')
