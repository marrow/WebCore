# encoding: utf-8

from __future__ import unicode_literals

from inspect import getargspec
from functools import partial

try:
    from inspect import getfullargspec as getargspec
except ImportError:
    pass

from marrow.util.compat import unicode, unicodestr



class CastExtension(object):
    """Typecast the arguments to your controllers using Python 3 function annotations."""

    provides = ['typecast']

    def __init__(self, encoding='utf-8', fallback='iso-8859-1'):
        super(CastExtension, self).__init__()
        self.handler = partial(unicodestr, encoding=encoding, fallback=fallback)

    def mutate(self, context, handler, args, kw):
        """Inspect and potentially mutate the given handler's arguments.

        The args list and kw dictionary may be freely modified, though invalid arguments to the handler will fail.
        """
        annotations = getattr(handler.__func__ if hasattr(handler, '__func__') else handler, '__annotations__', None)
        if not annotations:
            return
        
        for k in annotations:
            if annotations[k] == unicode:
                annotations[k] = self.handler
        
        argspec = getargspec(handler)
        arglist = list(argspec.args)
        
        # This should handle Python 3's method of binding, and Python 2's.
        if hasattr(handler.__call__, '__self__') or hasattr(handler, '__self__'):
            del arglist[0]

        for i, value in enumerate(list(args)):
            key = arglist[i]
            if key in annotations:
                args[i] = annotations[key](value)

        # Convert keyword arguments
        for key, value in list(kw.items()):
            if key in annotations:
                kw[key] = annotations[key](value)
