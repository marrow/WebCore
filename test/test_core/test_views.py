# encoding: utf-8

from __future__ import unicode_literals

from unittest import TestCase
from webob import Request
from web.core.context import Context
from web.core.compat import unicode
from web.core.view import WebViews


class DispatchBase(TestCase):
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
		self.view.register(unicode, cb)
		self.view.register(int, object)
		results = list(self.view("hi"))
		assert len(results) == 1
		assert results[0] is cb

