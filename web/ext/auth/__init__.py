# encoding: utf-8


class AuthenticationExtension(object):
    uses = ['template']
    needs = ['session']
    provides = ['auth', 'authentication', 'identity']
    
    def __init__(self, config):
        super(Extension, self).__init__()
    
    def prepare(self, context):
        """Prepare the variables from the context."""
        context.user = None
        context.acl = []
        context.namespace.user = context.user
        context.namespace.auth = predicates
    
    def dispatch(self, context, consumed, handler, is_endpoint):
        acl = getattr(handler, '__acl__', [])
        context.acl.append(acl)
    
    def before(self, context):
        """Validate the ACL."""
        pass
