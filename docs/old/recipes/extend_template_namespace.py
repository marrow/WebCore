# encoding: utf-8

"""Extending the template engine variable namespace to always include certain values is quite easy.

There are two places you can extend:

* The 'web' variable can be extended by assigning to the request context.
* Adding additonal top-level variables is accomplished by assigning to the 'namespace' attribute of the context.

Note that both of these sources are omitted from serialized rendering.  To add variables for serialization use the
__after__ handler within your controllers.  Pro tip:

    class MyController(object):
        def __init__(self, context):
            self.ctx = context
        
        def index(self):
            return 'json:', dict(hello="world")
        
        def __after__(self, result):
            result[1]['meaning'] = 42
"""


class SampleExtension(object):
    uses = [] # add soft dependencies or omit
    needs = [] # add hard dependencies or omit
    always = True # usually you don't want to be required to activate your own extensions
    provides = ['sample'] # can be omitted if always is True
    
    def __init__(self, config):
        """Executed to configure the extension."""
        super(SampleExtension, self).__init__()
    
    def prepare(self, context):
        """Executed during request set-up."""
        
        # The request context is used as the 'web' template variable.
        context.foo = 27
        
        # To extend the top-level namespace for temlpates:
        context.namespace.bar = 42
