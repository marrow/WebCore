# encoding: utf-8

from __future__ import unicode_literals

import pytest
from unittest import TestCase
from contextlib import contextmanager
from webob import Request

from web.core.application import Application
# from web.core.context import Context
from web.ext.acl import Predicate, always, never, Not, All, Any #, ContextMatch, ContextIn, ACLExtension


def nop(context=None):
	pass


@contextmanager
def must_be_called(n=None):
	"""Ensure the target function is called.
	
	If an `n` value is supplied, ensure the target is called that many times.
	"""
	called = []
	
	def must_call(context=None):
		called.append(context)
	
	yield must_call
	
	if n is None:
		assert len(called) > 0, "Predicate that must be called, was not."
	
	else:
		assert len(called) == n, "Predicate that must be called " + str(n) + " times was called " + \
				str(len(called)) + " times."


@contextmanager
def must_not_be_called():
	called = []
	
	def must_not_call(context=None):
		called.append(context)
	
	yield must_not_call
	
	assert len(called) == 0, "Predicate that must not be called, was."


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


class TestAllPredicate(TestCase):
	def test_all_nop(self):
		with must_be_called(3) as nop:
			assert All(nop, nop, nop)('fnord') is None
	
	def test_all_truthy(self):
		assert All(always, always, always)() is True
		
		with must_be_called(2) as nop:
			assert All(always, nop, nop)() is True
	
	def test_all_falsy(self):
		assert All(always, never, always)() is False
		
		with must_not_be_called() as canary:
			assert All(never, canary, canary)() is False
		
		with must_not_be_called() as canary:
			with must_be_called(1) as nop:
				assert All(nop, never, canary)() is False
		
		with must_not_be_called() as canary:
			assert All(always, never, canary)() is False
		
		with must_be_called(2) as nop:
			assert All(nop, nop, never)() is False
		
		with must_not_be_called() as canary:
			assert All(always, never, canary)() is False


def TestAnyPredicate(TestCase):
	def test_any_nop(self):
		with must_be_called(3) as nop:
			assert Any(nop, nop, nop)('fnord') is None
	
	def test_any_truthy(self):
		assert Any(always, always, always)() is True
		
		with must_be_called(2) as nop:
			assert Any(always, nop, nop)() is True
	
	def test_any_falsy(self):
		assert Any(always, never, always)() is False
		
		with must_not_be_called() as canary:
			assert Any(never, canary, canary)() is False
		
		with must_not_be_called() as canary:
			with must_be_called(1) as nop:
				assert Any(nop, never, canary)() is False
		
		with must_not_be_called() as canary:
			assert Any(always, never, canary)() is False
		
		with must_be_called(2) as nop:
			assert Any(nop, nop, never)() is False
		
		with must_not_be_called() as canary:
			assert Any(always, never, canary)() is False


class TestContextMatchPredicate(TestCase):
	pass


class TestContextInPredicate(TestCase):
	pass


class TestExtensionBehaviour(TestCase):
	def do(self, path, **data):
		app = Application(MockController)
		req = Request.blank(path)
		if data:
			req.content_type = 'application/json'
			if data:
				req.json = data
		return req.get_response(app)

