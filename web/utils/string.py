# encoding: utf-8

"""

"""

import re


__all__ = ['CStringIO', 'normalize', 'ellipsis']



class CStringIO(object):
    """A wrapper around cStringIO to allow for subclassing"""
    __csio = None

    def __init__(self, *a, **kw):
        try:
            from cStringIO import StringIO
        
        except ImportError:
            from StringIO import StringIO
        
        self.__csio = StringIO(*a, **kw)

    def __iter__(self):
        return self.__csio.__iter__()

    def next(self):
        return self.__csio.next()

    def close(self):
        return self.__csio.close()

    def isatty(self):
        return self.__csio.isatty()

    def seek(self, pos, mode=0):
        return self.__csio.seek(pos, mode)

    def tell(self):
        return self.__csio.tell()

    def read(self, n=-1):
        return self.__csio.read(n)

    def readline(self, length=None):
        return self.__csio.readline(length)

    def readlines(self, sizehint=0):
        return self.__csio.readlines(sizehint)

    def truncate(self, size=None):
        return self.__csio.truncate(size)

    def write(self, s):
        return self.__csio.write(s)

    def writelines(self, list):
        return self.__csio.writelines(list)

    def flush(self):
        return self.__csio.flush()

    def getvalue(self):
        return self.__csio.getvalue()


def normalize(name, collection=[], expression=re.compile('\W+')):
    """
    
    """
    base = expression.sub('-', name.lower())
    suffix = 0
    value = None
    
    while True:
        value = ("%s%s" % (base.strip('-'), ("-%d" % (suffix, )) if suffix else ""))
        if value not in collection: return value
        suffix += 1
    
    raise ValueError


def ellipsis(text, length):
    """
    Present a block of text of given length.
    
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
