#!/usr/bin/env python2.5
# encoding: utf-8

"""Basic XML-RPC service for YAPWF.

The classic "hello world" example, and simple mathematical formulae.
"""

from web.extras.rpc.xml import XMLRPCController



class Math(XMLRPCController):
    def add(self, a, b): return a + b
    def subtract(self, a, b): return a - b
    def multiply(self, a, b): return a * b
    def divide(self, a, b): return a / b


class RootController(XMLRPCController):
    math = Math()
    
    def hello(self, name="world"):
        return "Hello, %(name)s!" % dict(name=name)


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
