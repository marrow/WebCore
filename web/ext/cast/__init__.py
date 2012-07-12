# encoding: utf-8


class CastExtension(object):
    """Typecast the arguments to your controllers using Python 3 function annotations."""

    uses = []
    needs = []
    always = False
    never = False
    first = False
    last = False
    provides = []
    extensions = ()

    def __init__(self, config):
        """Executed to configure the extension.

        No actions must be performed here, only configuration management.

        You can also update the class attributes here.  It only really makes sense to add dependencies.
        """

        super(CastExtension, self).__init__()

    def mutate(self, context, handler, args, kw):
        """Inspect and potentially mutate the given handler's arguments.
        
        The args list and kw dictionary may be freely modified, though invalid arguments to the handler will fail.
        """
        annotations = getattr(handler.__func__ if hasattr(handler, '__func__') else handler, '__annotations__', None)
        if not annotations:
            return 
        
        context.log.info("MUTATING")
