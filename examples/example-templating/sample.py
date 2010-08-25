#!/usr/bin/env python2.5
# encoding: utf-8

from datetime import datetime

from web.core import Controller, request



class NestedController(Controller):
    def index(self):
        return "This is an awesome nested controller."


class RootController(Controller):
    nested = NestedController()
    
    def index(self):
        return 'genshi:templates.now', dict(now=datetime.now())
    
    def environ(self, *args, **kw):
        return 'templates.environ', dict(environ=request.environ, args=args, kw=kw)



if __name__ == '__main__':
    import logging
    from paste import httpserver
    from web.core import Application
    
    logging.basicConfig(level=logging.INFO)
    
    app = Application.factory(root=RootController, debug=False)
    
    httpserver.serve(app, host='127.0.0.1', port='8080')
