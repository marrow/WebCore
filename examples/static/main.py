#!/usr/bin/env python
# encoding: utf-8

"""A basic hello world application.

This can be simplified down to 5 lines in total; two import lines, two
controller lines, and one line to serve it.
"""

from web.core import Controller



class RootController(Controller):
    def index(self):
        return 'Hello world!'



if __name__ == '__main__':
    import logging
    from paste import httpserver
    from web.core import Application
    
    logging.basicConfig(level=logging.INFO)
    
    app = Application.factory(root=RootController, debug=True, **{'web.static': True, 'web.static.root': '/static'})
    
    httpserver.serve(app, host='127.0.0.1', port='8080')
