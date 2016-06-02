# encoding: utf-8

from __future__ import unicode_literals

from unittest import TestCase
from inspect import isclass
from webob import Request, Response
from webob.exc import HTTPNotModified

from web.core.application import Application


class TestApplicationParts(TestCase):
	def setUp(self):
		self.app = Application("Hi.")
	
	def test_application_attributes(self):
		assert isclass(self.app.RequestContext), "Non-class prepared request context."





def binary_endpoint(ctx): return b"Word."

def string_endpoint(ctx): return "Hi."

def empty_endpoint(ctx): return None

def response_endpoint(ctx): return Response(text="Yo.")

def binary_file_endpoint(ctx): return open('LICENSE.txt', 'rb')

def generator_endpoint(ctx):
	yield b'foo'
	yield b'bar'


class TestDefaulViews(object):
	def test_binary(self):
		app = Application(binary_endpoint)
		response = Request.blank('/').get_response(app)
		assert response.text == "Word."
	
	def test_string(self):
		app = Application(string_endpoint)
		response = Request.blank('/').get_response(app)
		assert response.text == "Hi."
	
	def test_none(self):
		app = Application(empty_endpoint)
		response = Request.blank('/').get_response(app)
		assert response.text == ""
		assert response.content_length == None  # Actually blank responses have no length.
	
	def test_response(self):
		app = Application(response_endpoint)
		response = Request.blank('/').get_response(app)
		assert response.text == "Yo."
	
	def test_file(self):
		app = Application(binary_file_endpoint)
		response = Request.blank('/').get_response(app)
		assert '2016' in response.text
	
	def test_generator(self):
		app = Application(generator_endpoint)
		response = Request.blank('/').get_response(app)
		assert 'foobar' in response.text


class MockController(object):
	def __init__(self, context):
		self._ctx = context
	
	def endpoint(self, a, b):
		return str(int(a) * int(b))
	
	def sum(self, v):
		return str(sum(int(i) for i in v))
	
	def notmod(self):
		raise HTTPNotModified()


class TestArgumentAndExceptionHandling(object):
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
	
	if __debug__:
		def test_catch_mismatch(self):
			assert self.do('/endpoint/4/3/9').status_int == 404

