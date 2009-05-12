# encoding: utf-8

"""
A collection of specialized dictionary subclasses.

TODO: Split this into its own package: every Python application and its dog seems to recreate these!
"""


log = __import__('logging').getLogger(__name__)
__all__ = ['adict', 'odict', 'mdict', 'ddict', 'idict']



class adict(dict):
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
        super(adict, self).__setitem__(key, value)
    
    def __getitem__(self, name):
        return super(adict, self).__getitem__(name)
    
    def __delitem__(self, name):
        super(adict, self).__delitem__(name)
    
    def __getattr__(self, name):
        if hasattr(self, name):
            return super(adict, self).__getattr__(name)
        
        return self.__getitem__(name)
    
    __setattr__ = __setitem__
    
    def copy(self):
        ch = self.__class__(self)
        return ch


class odict(dict):
    """Ordered dictionary implementation.

    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747
    """
    def __init__(self, data=None):
        dict.__init__(self, data or {})
        self._keys = dict.keys(self)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        dict.__setitem__(self, key, item)
        if key not in self._keys:
            self._keys.append(key)

    def __iter__(self):
        return iter(self._keys)

    def clear(self):
        dict.clear(self)
        self._keys = []

    def copy(self):
        d = odict()
        d.update(self)
        return d

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys[:]

    def pop(self, key, default=None):
        if key not in self:
            return default
        self._keys.remove(key)
        return dict.pop(self, key)

    def setdefault(self, key, failobj = None):
        dict.setdefault(self, key, failobj)
        if key not in self._keys:
            self._keys.append(key)

    def update(self, dict):
        for (key, val) in dict.items():
            self[key] = val

    def values(self):
        return map(self.get, self._keys)


class mdict(dict):
    """
    A dictionary that allows multiple values for a single key.
    """
    
    def __setitem__(self, key, value):
        self.setdefault(key, []).append(value)
    
    def iteritems(self):
        for key in self:
            values = dict.__getitem__(self, key)
            for value in values:
                yield (key, value)


class ddict(dict):
    """
    A dict that defaults non-existant values using a callback.
    """
    
    def __init__(self, creator, *args, **kw):
        self.creator = creator
        super(ddict, self).__init__(*args, **kw)
    
    def __missing__(self, key):
        self[key] = val = self.creator(key)
        return val


class idict(dict):
    """Dictionary, that has case-insensitive keys.

    Normally keys are retained in their original form when queried with
    .keys() or .items().  If initialized with preserveCase=0, keys are both
    looked up in lowercase and returned in lowercase by .keys() and .items().
    """
    """
    Modified recipe at
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66315 originally
    contributed by Sami Hangaslammi.
    """

    def __init__(self, dict=None, preserve=1):
        """Create an empty dictionary, or update from 'dict'."""
        self.data = {}
        self.preserve=preserve
        if dict:
            self.update(dict)

    def __delitem__(self, key):
        k=self._lowerOrReturn(key)
        del self.data[k]

    def _lowerOrReturn(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            return key.lower()
        else:
            return key

    def __getitem__(self, key):
        """Retrieve the value associated with 'key' (in any case)."""
        k = self._lowerOrReturn(key)
        return self.data[k][1]

    def __setitem__(self, key, value):
        """Associate 'value' with 'key'. If 'key' already exists, but
        in different case, it will be replaced."""
        k = self._lowerOrReturn(key)
        self.data[k] = (key, value)

    def has_key(self, key):
        """Case insensitive test whether 'key' exists."""
        k = self._lowerOrReturn(key)
        return self.data.has_key(k)
    __contains__=has_key

    def _doPreserve(self, key):
        if not self.preserve and (isinstance(key, str)
                                  or isinstance(key, unicode)):
            return key.lower()
        else:
            return key

    def keys(self):
        """List of keys in their original case."""
        return list(self.iterkeys())

    def values(self):
        """List of values."""
        return list(self.itervalues())

    def items(self):
        """List of (key,value) pairs."""
        return list(self.iteritems())

    def get(self, key, default=None):
        """Retrieve value associated with 'key' or return default value
        if 'key' doesn't exist."""
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default):
        """If 'key' doesn't exists, associate it with the 'default' value.
        Return value associated with 'key'."""
        if not self.has_key(key):
            self[key] = default
        return self[key]

    def update(self, dict):
        """Copy (key,value) pairs from 'dict'."""
        for k,v in dict.items():
            self[k] = v

    def __repr__(self):
        """String representation of the dictionary."""
        items = ", ".join([("%r: %r" % (k,v)) for k,v in self.items()])
        return "InsensitiveDict({%s})" % items

    def iterkeys(self):
        for v in self.data.itervalues():
            yield self._doPreserve(v[0])

    def itervalues(self):
        for v in self.data.itervalues():
            yield v[1]

    def iteritems(self):
        for (k, v) in self.data.itervalues():
            yield self._doPreserve(k), v

    def popitem(self):
        i=self.items()[0]
        del self[i[0]]
        return i

    def clear(self):
        for k in self.keys():
            del self[k]

    def copy(self):
        return InsensitiveDict(self, self.preserve)

    def __len__(self):
        return len(self.data)

    def __eq__(self, other):
        for k,v in self.items():
            if not (k in other) or not (other[k]==v):
                return 0
        return len(self)==len(other)
