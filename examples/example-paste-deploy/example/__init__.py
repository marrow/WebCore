# encoding: utf-8

import web
from web.core import Controller



class RootController(Controller):
    def index(self):
        return 'Hello world!'
    
    def hello(self, name):
        return "Hello, %(name)s!" % dict(name=name)
    
    def error(self):
        raise ValueError
    
    def notfound(self):
        raise web.core.http.HTTPNotFound()
    
    def handler(self, code):
        return 'Pretty error page for HTTP %s.' % (code, )
    
    def time(self):
        from datetime import datetime
        return 'example.templates.now', dict(now=datetime.now())
