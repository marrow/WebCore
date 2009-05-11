# encoding: utf-8

__all__ = ['Attributed', 'Defaulted']


class Attributed(dict):
    """A dictionary with attribute-style access. It maps attribute access to the real dictionary."""
    
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
    
    def __getstate__(self):
        return self.__dict__.items()
    
    def __setstate__(self, items):
        for key, val in items:
            self.__dict__[key] = val
    
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, dict.__repr__(self))
    
    def __setitem__(self, key, value):
        return super(Attributed, self).__setitem__(key, value)
    
    def __getitem__(self, name):
        return super(Attributed, self).__getitem__(name)
    
    def __delitem__(self, name):
        return super(Attributed, self).__delitem__(name)
    
    __getattr__ = __getitem__
    __setattr__ = __setitem__
    
    def copy(self):
        ch = self.__class__(self)
        return ch


class Defaulted(Attributed):
    def __init__(self, default, *args, **kw):
        super(Defaulted, self).__init__(self, *args, **kw)
    