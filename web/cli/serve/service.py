# encoding: utf-8

from __future__ import unicode_literals, print_function

from marrow.util.object import load_object as load


class Marrow(object):
    def __init__(self, **config):
        try:
            self.backend = load('marrow.server.http:HTTPServer')
        except ImportError:
            raise ImportError("Unable to import the Marrow web server.  To correct, run:\n\tpip install marrow.server.http")
        
        self.config = config
    
    def __call__(self, app):
        self.server = self.backend(application=app, **self.config)
        return self
    
    def start(self):
        self.server.start()
    
    def stop(self):
        pass
    
    def restart(self):
        pass
    
    def reload(self):
        pass
