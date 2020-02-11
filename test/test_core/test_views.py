# encoding: utf-8

from unittest import TestCase
from webob import Request
from web.core.context import Context
from web.core.view import WebViews


class TestWebViews(TestCase):
	def setUp(self):
		self._ctx = Context(
				request = Request.blank('/foo/bar'),
				extension = Context(signal=Context(dispatch=[])),
				dispatched = False,
				callback = False,
				events = [],
			)
		self.view = self._ctx.view = WebViews(self._ctx)
		self._ctx.environ = self._ctx.request.environ
	
	def mock_view(self, context, value):
		context.value = value
	
	def test_registration(self):
		assert dict not in self.view._map
		self.view.register(dict, self.mock_view)
		assert dict in self.view._map
		assert self.view._map.get(dict) == self.mock_view
	
	def test_resolution(self):
		cb = self.mock_view
		self.view.register(str, cb)
		self.view.register(int, object)
		results = list(self.view("hi"))
		assert len(results) == 1
		assert results[0] is cb
	
	def test_repr(self):
		assert repr(self.view) == "WebViews(0)"
		self.view.register(dict, self.mock_view)
		assert repr(self.view) == "WebViews(1)"
