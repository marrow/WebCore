# encoding: utf-8

from __future__ import unicode_literals

from threading import local
from inspect import getargspec
from functools import partial

from marrow.util.object import load_object
from marrow.util.compat import unicode, unicodestr



class ThreadLocalExtension(object):
    """Provide the current context as a thread local global."""

    first = True
    uses = ['request']
    provides = ['threadlocal']

    def __init__(self, where='web:local'):
        super(ThreadLocalExtension, self).__init__()
        
        self.where = where
        self.local = None
        self.preserve = False
    
    def _lookup(self):
        module, _, name = self.where.rpartition(':')
        module = load_object(module)
        
        return module, name
    
    def start(self, context):
        module, name = self._lookup()
        
        if hasattr(module, name):
            self.local = getattr(module, name)
            self.preserve = True
        else:
            self.local = local()
            setattr(module, name, self.local)
    
    def stop(self, context):
        self.local = None
        
        if self.preserve:
            return
        
        module, name = self._lookup()
        delattr(module, name)
    
    def prepare(self, context):
        self.local.context = context
