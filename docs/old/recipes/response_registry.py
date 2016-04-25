# encoding: utf-8

"""Adding additional return value handlers is easy."""

from web.core.response import register


class MyObject(object):
    pass


def handler(context, result):
    pass # do something to the context.response


class SampleExtension(object):
    always = True # usually you don't want to be required to activate your own extensions
    provides = ['sample'] # can be omitted if always is True
    
    def __init__(self, config):
        """Executed to configure the extension."""
        super(SampleExtension, self).__init__()
    
    def start(self):
        # Register our custom handler; be sure to pick your type carefully!
        register(handler, MyObject)
