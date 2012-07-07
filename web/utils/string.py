# encoding: utf-8
# pragma: no cover

import warnings

from marrow.util.text import normalize, ellipsis


__all__ = ['CStringIO', 'normalize', 'ellipsis']


warnings.warn("Use of web.utils.string is deprecated, use marrow.util.text instead.", DeprecationWarning)


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

    def read(self, n= -1):
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
