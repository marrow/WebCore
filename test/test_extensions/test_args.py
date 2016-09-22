# encoding: utf-8

from __future__ import unicode_literals

import json
from unittest import TestCase
from webob import Request
from webob.exc import HTTPNotModified

from web.core.application import Application


class MockController(object):
	def __init__(self, context):
		self._ctx = context
	
	def endpoint(self, a, b):
		return str(int(a) * int(b))
	
	def sum(self, v):
		return str(sum(int(i) for i in v))
	
	def notmod(self):
		raise HTTPNotModified()
	
	def rich(self, data):
		return json.dumps({'result': data})


class TestArgumentAndExceptionHandling(TestCase):
	def do(self, path):
		app = Application(MockController)
		req = Request.blank(path)
		return req.get_response(app)
	
	def test_positional(self):
		assert self.do('/endpoint/4/8').text == "32"
	
	def test_keyword(self):
		assert self.do('/endpoint?a=2&b=12').text == "24"
	
	def test_repeated(self):
		assert self.do('/sum?v=1&v=1&v=2&v=3&v=5').text == "12"
	
	def test_httpexception_catch(self):
		assert self.do('/notmod').status_int == 304
	
	def test_catch_mismatch(self):
		assert self.do('/endpoint/4/3/9').status_int == 404
	
	def test_array_basic(self):
		assert self.do('/rich?data=1&data=2').json['result'] == ['1', '2']
	
	def test_explicit_array(self):
		assert self.do('/rich?data[]=1').json['result'] == ['1']
		assert self.do('/rich?data[]=1&data[]=2').json['result'] == ['1', '2']
	
	def test_indexed_array(self):
		assert self.do('/rich?data.3=3&data.1=1&data.2=2').json['result'] == ['1', '2', '3']
	
	def test_dictionary(self):
		assert self.do('/rich?data.bar=1&data.baz=2').json['result'] == {'bar': '1', 'baz': '2'}


