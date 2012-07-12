# encoding: utf-8

from inspect import getargspec, ismethod

try:
    from inspect import getfullargspec as getargspec
except ImportError:
    pass


class CastExtension(object):
    """Typecast the arguments to your controllers using Python 3 function annotations."""

    provides = ['typecast']

    def __init__(self, config):
        super(CastExtension, self).__init__()

    def mutate(self, context, handler, args, kw):
        """Inspect and potentially mutate the given handler's arguments.

        The args list and kw dictionary may be freely modified, though invalid arguments to the handler will fail.
        """
        annotations = getattr(handler.__func__ if hasattr(handler, '__func__') else handler, '__annotations__', None)
        if not annotations:
            return 

        argspec = getargspec(handler)
        arglist = list(argspec.args)
        
        if arglist[0] == 'self':
            del arglist[0]

        for i, value in enumerate(list(args)):
            key = arglist[i]
            if key in annotations:
                args[i] = annotations[key](value)

        # Convert keyword arguments
        for key, value in list(kw.items()):
            if key in annotations:
                kw[key] = annotations[key](value)
