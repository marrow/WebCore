# encoding: utf-8

from unittest import TestCase

from web.utils.object import *
from web.utils.dictionary import *


class TestPropertyIterator(TestCase):
    class MyObj(object):
        def __init__(self, name):
            self.name = name
    
    def test_property_iterator(self):
        objs = [self.MyObj('a'), self.MyObj('b'), self.MyObj('c')]
        self.assertEqual([i for i in yield_property(objs, 'name')], ['a', 'b', 'c'])


class TestCounterMeta(TestCase):
    class MyObj(object):
        __metaclass__ = CounterMeta
    
    def test_counter_meta(self):
        objs = [self.MyObj(), self.MyObj(), self.MyObj()]
        self.assertEqual([i._counter for i in objs], [0, 1, 2])


class TestAttributeDictionary(TestCase):
    def test_empty_creation(self):
        d = adict()
        assert not d
    
    def test_populated_creation(self):
        d = adict(name='value')
        self.assertEqual(d['name'], 'value')
        
        d = adict({'name': 'value'})
        self.assertEqual(d['name'], 'value')
    
    def test_attribute_assignment(self):
        d = adict()
        d.name = 'value'
        assert hasattr(d, 'name')
        self.assertEqual(d['name'], 'value')
    
    def test_attribute_read(self):
        d = adict()
        d.name = 'value'
        assert d.name == 'value'
    
    def test_repr(self):
        d = adict()
        assert repr(d) == 'adict({})'
        
        d.name = 'value'
        self.assertEqual(repr(d), "adict({'name': 'value'})")
    
    def test_delete(self):
        d = adict(name='value')
        del d.name
        
        self.assertEqual(repr(d), 'adict({})')
