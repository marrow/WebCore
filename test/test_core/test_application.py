# encoding: utf-8

import pytest

from unittest import TestCase
from inspect import isclass

from web.core.application import Application

from marrow.util.bunch import Bunch


class TestApplicationParts(TestCase):
    def setUp(self):
        self.app = Application("Hi.")
    
    def test_application_attributes(self):
        self.assertTrue(isclass(self.app.Context), "Non-class context.")
        self.assertIsInstance(self.app.Context.config, Bunch)
        self.assertIsInstance(self.app.Context.config.extensions, list)
    
    def test_prepare_configuration(self):
        configuration = dict()
        processed = self.app.prepare_configuration(configuration)
        
        self.assertIsInstance(processed, Bunch)
        self.assertTrue('extensions' in processed, "Missing extensions sub-config.")
    
    def test_context_factory(self):
        root = object()
        config = Bunch()
        
        Context = self.app.context_factory(root, config)
        
        self.assertTrue(isclass(Context), "Context factory returned non-class.")
        
        self.assertIs(Context.root, root)
        self.assertIs(Context.config, config)
        self.assertIs(Context.app, self.app)
    
    def test_context_behaviour(self):
        Context = self.app.context_factory(object(), Bunch())
        
        context = Context()
        
        context.foo = 27
        self.assertEquals(context.foo, 27)
        
        self.assertIn('foo', list(i for i, j in context))
        
        parts = [i for i, j in context]
        for i in ['app', 'config', 'foo', 'log', 'root']:
            self.assertIn(i, parts)


class TestApplicationExtensions(TestCase):
    class FaultyException(object):
        needs = ('impossible', )
    
    def test_missing_requirement(self):
        with pytest.raises(LookupError):
            Application('Hi.', extensions=[self.FaultyException()])
