# encoding: utf-8

from __future__ import unicode_literals

import pytest
from unittest import TestCase
from webob import Request

from web.core.application import Application
# from web.core.context import Context
from web.ext.acl import Predicate, always, never, Not, All, Any #, ContextMatch, ContextIn, ACLExtension


def nop(context=None):
	pass


class MockController:
	pass


class TestBasicPredicateBehaviour(TestCase):
	def test_bare_predicate_fails(self):
		with pytest.raises(NotImplementedError):
			Predicate()()
	
	def test_always(self):
		assert always() is True
	
	def test_never(self):
		assert never() is False
	
	def test_not(self):
		assert Not(always)() is False
		assert Not(never)() is True
		assert Not(nop)(27) is None
	
	def test_all(self):
		assert All(nop, nop, nop)() is None
		assert All(always, always, always)() is True
		assert All(never, never, never)() is False
		
		assert All(nop, never, never)() is False
		assert All(never, nop, never)() is False
		assert All(never, never, nop)() is False
		
		assert All(nop, never, always)() is False
		assert All(always, nop, never)() is False
		assert All(never, always, nop)() is False
		
		assert All(nop, nop, always)(27) is True
		assert All(nop, nop, never)(27) is False
	
	def test_any(self):
		assert Any(nop, nop, nop)() is None
		assert Any(always, always, always)() is True
		assert Any(never, never, never)() is False
		
		assert Any(nop, never, never)() is False
		assert Any(never, nop, never)() is False
		assert Any(never, never, nop)() is False
		
		assert Any(nop, never, always)() is False
		assert Any(always, nop, never)() is True
		assert Any(never, always, nop)() is False
		
		assert Any(nop, nop, always)(27) is True
		assert Any(nop, nop, never)(27) is False


class TestExtensionBehaviour(TestCase):
	def do(self, path, **data):
		app = Application(MockController)
		req = Request.blank(path)
		if data:
			req.content_type = 'application/json'
			if data:
				req.json = data
		return req.get_response(app)

