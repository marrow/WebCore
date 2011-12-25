#.encoding: utf-8


class AuthenticationExtension(object):
    uses = ['template']
    needs = ['session']
    provides = ['auth', 'authentication', 'identity']
    
    def __init__(self, config):
        super(Extension, self).__init__()
    
    def prepare(self, context):
        context.user = None
        context.namespace.user = context.user
        context.namespace.auth = predicates
