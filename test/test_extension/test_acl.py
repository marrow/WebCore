# encoding: utf-8

from __future__ import unicode_literals

import pytest
from unittest import TestCase
from webob import Request

from web.core.application import Application
from web.core.context import Context
from web.ext.acl import Predicate, Not, All, Any, ContextMatch, ContextIn, ACLExtension



class TestPredicateBehaviour(TestCase):
	def test_bare_predicate_fails(self):
		with pytest.raises(NotImplementedError):
			Predicate()(None)


class TestExtensionBehaviour(TestCase):
	def do(self, path, **data):
		app = Application(MockController)
		req = Request.blank(path)
		if data:
			req.content_type = 'application/json'
			if data:
				req.json = data
		return req.get_response(app)

