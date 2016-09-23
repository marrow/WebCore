# encoding: utf-8

from __future__ import unicode_literals

from unittest import TestCase
from webob import Request, Response

from web.core.application import Application


def binary_endpoint(ctx): return b"Word."

def string_endpoint(ctx): return "Hi."

def empty_endpoint(ctx): return None

def response_endpoint(ctx): return Response(text="Yo.")

def binary_file_endpoint(ctx): return open('LICENSE.txt', 'rb')

def generator_endpoint(ctx):
	yield b'foo'
	yield b'bar'


class TestDefaulViews(TestCase):
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

