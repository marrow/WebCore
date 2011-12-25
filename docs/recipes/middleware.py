# encoding: utf-8

"""Adding middleware to the stack is fairly straight-forward."""


class MiddlewareExtension(object):
    uses = [] # add soft dependencies or omit
    needs = [] # add hard dependencies or omit
    always = True # usually you don't want to be required to activate your own extensions
    provides = ['sample'] # can be omitted if always is True
    
    def __init__(self, config):
        """Executed to configure the extension."""
        super(MiddlewareExtension, self).__init__()
        self.config = config
    
    def __call__(self, app):
        return MyMiddleware(app, self.config)
