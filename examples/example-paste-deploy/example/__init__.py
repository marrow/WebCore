# encoding: utf-8

from web.core import Controller



class RootController(Controller):
    def index(self):
        return 'Hello world!'
    
    def hello(self, name):
        return "Hello, %(name)s!" % dict(name=name)
    
    def error(self):
        raise ValueError
    
    def time(self):
        from datetime import datetime
        return 'example.templates.now', dict(now=datetime.now())
