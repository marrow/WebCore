# encoding: utf-8

try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from web.core.response import ResponseRegistry


class TestResponseRegistry(TestCase):
    def setUp(self):
        self.registry = ResponseRegistry()
    
    def sample_callable_always(self, context, response):
        return True
    
    def sample_callable_never(self, context, response):
        return False
    
    def sample_callable_conditional(self, context, response):
        return context
    
    def test_registration(self):
        self.registry.register(True, False, None)
        
        self.assertEquals(self.registry.registry, [((False, None), True)])
        self.assertIs(self.registry.registry[0][0][0], False)
        self.assertIs(self.registry.registry[0][0][1], None)
        self.assertIs(self.registry.registry[0][1], True)
    
    def test_lookup(self):
        self.registry.register(self.sample_callable_always, type(True))
        
        self.assertTrue(self.registry(None, True))
        self.assertFalse(self.registry(None, None))
