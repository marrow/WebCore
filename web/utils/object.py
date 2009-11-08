# encoding: utf-8

"""

"""


from pkg_resources import resource_filename

__all__ = ['yield_property', 'CounterMeta', 'get_dotted_object']



def yield_property(iterable, name):
    for i in iterable: yield getattr(i, name, None)


class CounterMeta(type):
    """Declarative style helper.
    
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


def get_dotted_object(target):
    """This helper function loads an object identified by a dotted-notation string.
    
    For example:
    
        # Load class Foo from example.objects
        get_dotted_object('example.objects:Foo')
    """
    parts, target = target.split(':') if ':' in target else (target, None)
    module = __import__(parts)
    
    for part in parts.split('.')[1:] + ([target] if target else []):
        module = getattr(module, part)
    
    return module
        