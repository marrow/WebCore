# encoding: utf-8

from unittest import TestCase
from inspect import isclass
from webob import Request, Response

from web.core.application import Application


class TestApplicationParts(TestCase):
	def setUp(self):
		self.app = Application("Hi.")
	
	def test_application_attributes(self):
		assert isclass(self.app.RequestContext), "Non-class prepared request context."


class TestStaticEndpoints(object):
	def test_string(self):
		app = Application(lambda ctx: "Hi.")
		response = Request.blank('/').get_response(app)
		assert response.text == "Hi."
	
	def test_none(self):
		app = Application(lambda ctx: None)
		response = Request.blank('/').get_response(app)
		assert response.text == ""
		assert response.content_length == 0
	
	def test_response(self):
		app = Application(lambda ctx: Response(text="Yo."))
		response = Request.blank('/').get_response(app)
		assert response.text == "Yo."
	
	def test_file(self):
		app = Application(lambda ctx: open('LICENSE.txt', 'rb'), logging=dict(level='debug'))
		response = Request.blank('/').get_response(app)
		assert '2016' in response.text
	
	def test_generator(self):
		app = Application(lambda ctx: (i for i in ['foo', 'bar']))
		response = Request.blank('/').get_response(app)
		assert 'foobar' in response.text

