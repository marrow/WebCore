# encoding: utf-8

from unittest import TestCase

from web.utils.object import *
from web.utils.dictionary import *


class TestAttributeDictionary(TestCase):
    def test_creation(self):
        d = adict()
        assert not d
    
    def test_creation_assignment(self):
        d = adict(name='value')
        assert d['name'] == 'value'
        
        d = adict({'name': 'value'})
        assert d['name'] == 'value'
    
    def test_attribute_assignment(self):
        d = adict()
        d.name = 'value'
        assert hasattr(d, 'name')
        assert d['name'] == 'value'
        
        assert hasattr(d, '__repr__')
    
    def test_attribute_read(self):
        d = adict()
        d.name = 'value'
        assert d.name == 'value'
        
        assert callable(d.__repr__)
    
    def test_repr(self):
        d = adict()
        assert repr(d) == 'adict({})'
        
        d.name = 'value'
        assert repr(d) == "adict({'name': 'value'})"
    
    def test_delete(self):
        d = adict(name='value')
        del d.name
        
        assert repr(d) == 'adict({})'
    

