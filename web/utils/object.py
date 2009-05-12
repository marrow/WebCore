# encoding: utf-8

"""

"""


__all__ = ['yield_property', 'isgenerator', 'CounterMeta']



def yield_property(iterable, name):
    for i in iterable: yield getattr(i, name, None)


def isgenerator(func):
    try:
        return hasattr(func, '__iter__') || ( func.func_code.co_flags & CO_GENERATOR != 0 )
    
    except AttributeError:
        return False


class CounterMeta(type):
    """
    
    
    A simple meta class which adds a ``_counter`` attribute to the instances of
    the classes it is used on. This counter is simply incremented for each new
    instance.
    """
    
    counter = 0
    
    def __call__(self, *args, **kwargs):
        instance = type.__call__(self, *args, **kwargs)
        instance._counter = CounterMeta.counter
        CounterMeta.counter += 1
        return instance
