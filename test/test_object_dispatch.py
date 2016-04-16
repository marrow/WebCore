# encoding: utf-8

from __future__ import unicode_literals

import pytest

from webob import Request
from web.core import Application

from sample import function, Simple, CallableShallow, CallableDeep, CallableMixed


def do(root, path_):
	app = Application(root)
	req = Request.blank(path_)
	return req.get_response(app)


class TestFunctionDispatch(object):
	def test_root_path_resolves_to_function(self):
		assert do(function, '/').text == 'function /'
	
	def test_deep_path_resolves_to_function(self):
		assert do(function, '/foo/bar/baz').text == 'function /foo/bar/baz'


class TestSimpleDispatch(object):
	def test_protected_init_method(self):
		assert do(Simple, '/__init__').status_int == 404
	
	def test_protected_simple_value(self):
		assert do(Simple, '/_protected').status_int == 404
	
	def test_static_attribute(self):
		assert do(Simple, '/static').text == "foo"
	
	def test_shallow_class_lookup(self):
		with pytest.raises(TypeError):
			do(Simple, '/foo')
	
	def test_deep_class_lookup(self):
		with pytest.raises(TypeError):
			do(Simple, '/foo/bar')
	
	def test_partial_incomplete_lookup(self):
		assert do(Simple, '/foo/bar/diz').status_int == 404
	
	def test_deepest_endpoint_lookup(self):
		assert do(Simple, '/foo/bar/baz').text == "baz"


class TestCallableShallowDispatch(object):
	def test_root_path_resolves_to_instance(self):
		assert do(CallableShallow, '/').text == "/"
		
	def test_deep_path_resolves_to_instance(self):
		assert do(CallableShallow, '/foo/bar/baz').text == "/foo/bar/baz"


class TestCallableDeepDispatch(object):
	def test_shallow_class_lookup(self):
		with pytest.raises(TypeError):
			do(CallableDeep, '/foo')
	
	def test_deep_callable_class_lookup(self):
		assert do(CallableDeep, '/foo/bar').text == "/foo/bar"
	
	def test_incomplete_lookup(self):
		assert do(CallableDeep, '/foo/diz').status_int == 404
	
	def test_beyond_callable_class_lookup(self):
		assert do(CallableDeep, '/foo/bar/baz').text == "/foo/bar/baz"


class TestCallableMixedDispatch(object):
	def test_callable_root(self):
		assert do(CallableMixed, '/').text == "/"
	
	def test_shallow_class_lookup(self):
		with pytest.raises(TypeError):
			do(CallableMixed, '/foo')
	
	def test_deep_callable_class_lookup(self):
		with pytest.raises(TypeError):
			do(CallableMixed, '/foo/bar')
	
	def test_incomplete_lookup(self):
		assert do(CallableMixed, '/foo/diz').status_int == 404
	
	def test_deepest_endpoint_lookup(self):
		assert do(CallableMixed, '/foo/bar/baz').text == "baz"

