#!/usr/bin/env python
# encoding: utf-8

"""Test the TurboMail Message class."""


import unittest
from cmf.util import *

import logging
logging.disable(logging.WARNING)


class Rig(object):
    def __init__(self, name):
        self.name = name


class TestNormalization(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(normalize('This is my test.'), "this-is-my-test")
        self.assertEqual(normalize('Funky ending...'), "funky-ending")
    
    def test_simple_collisions(self):
        used = ['foo', 'bar', 'bar-1', 'baz']
        self.assertEqual(normalize('diz', used), "diz")
        self.assertEqual(normalize('foo', used), "foo-1")
        self.assertEqual(normalize('bar', used), "bar-2")
    
    def test_property_collision(self):
        used = [Rig('foo'), Rig('bar'), Rig('bar-1'), Rig('baz')]
        
        self.assertEqual(normalize('diz', yield_property(used, 'name')), "diz")
        self.assertEqual(normalize('foo', yield_property(used, 'name')), "foo-1")
        self.assertEqual(normalize('bar', yield_property(used, 'name')), "bar-2")
        
