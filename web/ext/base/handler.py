# encoding: utf-8

import types
import collections

from marrow.wsgi.objects import Response
from marrow.util.compat import binary, unicode


__all__ = ['serve', 'empty', 'response', 'primary']



def types(*types):
    def decorator(fn):
        fn.types = types
        return fn
    
    return decorator


@types(Response)
def response(context, result):
    context.response = result


@types(binary, unicode, list, types.GeneratorType, collections.Iterable)
def primary(context, result):
    context.response.body = result


@types(type(None))
def empty(context, result):
    context.response.length = 0
    context.response.body = None


@types(file)
def serve(context, result):
    # To the "right" thing.
    # Seek to the end then tell to get length.
    # Check the config from the context to determine use of X-Sendfile.
    context.response.body = result
