# encoding: utf-8

from marrow.interface import Interface, method


class IExtension(Interface):
    __init__ = method(args=1)
    start = method()
    stop = method()
    __call__ = method(args=2)
