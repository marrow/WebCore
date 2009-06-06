from web.core                                   import Controller, request, response


class RootController(Controller):
    def index(self):
        return 'Hello world!'
    
    def hello(self, name):
        return "Hello, %(name)s!" % dict(name=name)
    
    def error(self):
        raise ValueError
    
    def time(self):
        from datetime import datetime
        return 'yapwfexamples.templates.template', dict(now=datetime.now())
