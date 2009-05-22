# encoding: utf-8

"""Utility functions and classes used by TurboCMF."""

import re

__all__ = ['AttrDict', 'CounterMeta', 'normalize', 'yield_property', 'ellipsis']


class AttrDict(dict):
    """A dictionary with attribute-style access. It maps attribute access to the real dictionary."""
    
    def __init__(self, init={}):
        dict.__init__(self, init)
    
    def __getstate__(self):
        return self.__dict__.items()
    
    def __setstate__(self, items):
        for key, val in items:
            self.__dict__[key] = val
    
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, dict.__repr__(self))
    
    def __setitem__(self, key, value):
        return super(AttrDict, self).__setitem__(key, value)
    
    def __getitem__(self, name):
        return super(AttrDict, self).__getitem__(name)
    
    def __delitem__(self, name):
        return super(AttrDict, self).__delitem__(name)
    
    __getattr__ = __getitem__
    __setattr__ = __setitem__
    
    def copy(self):
        ch = AttrDict(self)
        return ch


class CounterMeta(type):
    '''
    A simple meta class which adds a ``_counter`` attribute to the instances of
    the classes it is used on. This counter is simply incremented for each new
    instance.
    '''
    counter = 0
    
    def __call__(self, *args, **kwargs):
        instance = type.__call__(self, *args, **kwargs)
        instance._counter = CounterMeta.counter
        CounterMeta.counter += 1
        return instance


NORMALIZE_EXPRESSION = re.compile('\W+')
def normalize(name, collection=[]):
    base = NORMALIZE_EXPRESSION.sub('-', name.lower())
    suffix = 0
    
    while True:
        if ("%s%s" % (base.strip('-'), ("-%d" % (suffix, )) if suffix else "")) not in collection: break
        suffix += 1
    
    return ("%s%s" % (base.strip('-'), ("-%d" % (suffix, )) if suffix else ""))


def yield_property(iterable, name):
    for i in iterable: yield getattr(i, name, None)


def ellipsis(text, length):
    """Present a block of text of given length.

    If the length of available text exceeds the requested length, truncate and
    intelligently append an ellipsis.
    """
    if len(text) > length:
        pos = text.rfind(" ", 0, length)
        if pos < 0:
            return text[:length].rstrip(".") + "..."
        else:
            return text[:pos].rstrip(".") + "..."
    else:
        return text