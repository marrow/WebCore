# encoding: utf-8

from __future__ import unicode_literals

from webob import Request, Response

from web.core.application import Application
from web.core.util import safe_name


def binary_endpoint(ctx): return b"Word."

def string_endpoint(ctx): return "Hi."

def empty_endpoint(ctx): return None

def response_endpoint(ctx): return Response(text="Yo.")

def binary_file_endpoint(ctx): return open('LICENSE.txt', 'rb')

def generator_endpoint(ctx):
	yield b'foo'
	yield b'bar'


class MockController(object):
	def __init__(self, context):
		self._ctx = context
	
	def here(self):
		return str(self._ctx.path.current)
	
	def paths(self):
		return ', '.join(str(i.path) for i in self._ctx.path)
	
	def handlers(self):
		return ', '.join(safe_name(i.handler) for i in self._ctx.path)


class TestBreadcrumbPath(object):
	def test_here(self):
		app = Application(MockController)
		response = Request.blank('/here').get_response(app).text
		assert response == '/here'
	
	def test_breadcrumb_list_paths(self):
		app = Application(MockController)
		response = Request.blank('/paths').get_response(app).text
		assert response == "., /paths"
	
	def test_breadcrumb_list_handlers(self):
		app = Application(MockController)
		response = Request.blank('/handlers').get_response(app).text
		assert response == "test_base:MockController, test_base:MockController.handlers"


class TestDefaultViews(object):
	def do(self, endpoint):
		app = Application(endpoint)
		return Request.blank('/').get_response(app)
	
	def test_binary(self):
		assert self.do(binary_endpoint).text == "Word."
	
	def test_string(self):
		assert self.do(string_endpoint).text == "Hi."
	
	def test_none(self):
		response = self.do(empty_endpoint)
		assert response.text == ""
		assert response.content_length == None  # Actually blank responses have no length.
	
	def test_response(self):
		assert self.do(response_endpoint).text == "Yo."
	
	def test_file(self):
		assert '2006' in self.do(binary_file_endpoint).text
	
	def test_generator(self):
		assert 'foobar' in self.do(generator_endpoint).text

