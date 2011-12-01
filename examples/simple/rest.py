#!/usr/bin/env python
# encoding: utf-8

"""A restful hello world application."""

from web.core import Controller, RESTMethod



class Index(RESTMethod):
    def get(self):
        return "Hello world!"
    
    def post(self, name="world"):
        return "Hello %s!" % (name, )



class RootController(Controller):
    index = Index()



if __name__ == '__main__':
    import logging
    from paste import httpserver
    from web.core import Application
    
    logging.basicConfig(level=logging.INFO)
    
    app = Application.factory(root=RootController, debug=False, **{
            'web.sessions': False,
            'web.widgets': False,
            'web.sessions': False,
            'web.profile': False,
            'web.static': False,
            'web.compress': False
        })
    
    httpserver.serve(app, host='127.0.0.1', port='8080')
