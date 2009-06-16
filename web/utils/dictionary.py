# encoding: utf-8

"""
A collection of specialized dictionary subclasses.
"""


log = __import__('logging').getLogger(__name__)
__all__ = ['adict']



class adict(dict):
    """A dictionary with attribute-style access. It maps attribute access to the real dictionary."""
    
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
    
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, super(adict, self).__repr__())
    
    def __delattr__(self, name):
        del self[name]
    
    def __getattr__(self, name):
        if name in self.__dict__: return self.__dict__.get(name)
        return self[name]
    
    def __setattr__(self, name, value):
        self[name] = value
