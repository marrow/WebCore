#!/usr/bin/env python2.5
# encoding: utf-8

"""Combined HTML and XML-RPC service for YAPWF.

The classic "hello world" example on drugs.
"""

from web.core import Controller
from web.extras.rpc.xml import XMLRPCController



class HelloMethods(object):
    def hello(self, name="world"):
        return "Hello, %(name)s!" % dict(name=name)


class HelloXMLRPC(HelloMethods, XMLRPCController):
    pass


class RootController(HelloMethods, Controller):
    api = HelloXMLRPC()
    
    def index(self):
        return self.hello()


if __name__ == '__main__':
    import logging
    from paste import httpserver
    from web.core import Application
    
    logging.basicConfig(level=logging.DEBUG)
    
    app = Application.factory(root=RootController, debug=False, **{
            'web.buffet': False,
            'web.widgets': False,
            'web.sessions': False,
            'web.profile': False,
            'web.static': False,
            'web.compress': False
        })
    
    httpserver.serve(app, host='127.0.0.1', port='8080')
