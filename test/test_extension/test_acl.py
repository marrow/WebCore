# encoding: utf-8

from __future__ import unicode_literals

import pytest
from contextlib import contextmanager
from webob import Request

from web.core.application import Application
from web.core.context import Context
from web.ext.acl import when, ACLResult, ACLExtension
from web.ext.acl import Predicate, always, never
from web.ext.acl import Not, First, All, Any
from web.ext.acl import ContextMatch, ContextContains


# # Support Machinery

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
	"""Ensure the target function is never called."""
	called = []
	
	def must_not_call(context=None):
		called.append(context)
	
	yield must_not_call
	
	assert len(called) == 0, "Predicate that must not be called, was."


@pytest.fixture
def context():
	"""Sometimes, you just need an empty context."""
	yield Context()


@pytest.fixture
def admin():
	"""The "administrative user" example for ContextMatch."""
	yield ContextMatch(True, 'user.admin', True)


@pytest.fixture
def reviewer():
	"""The "content reviewer" example for ContextIn."""
	yield ContextContains(True, 'user.role', 'reviewer')


class MockController:
	def __init__(self, context):
		self._ctx = context
	
	def __call__(self):
		return "Hi."


@when(always)
class Grant(MockController):
	pass


@when(always)
class EarlyGrant(MockController):
	@when(never)
	def __call__(self):
		return "Hi."


@when(never)
class EarlyDeny(MockController):
	@when(always)
	def __call__(self):
		return "Hi."



# # Tests


class TestPredicateHelpers(object):
	def test_when_decorator(self):
		@when(None)
		def inner(): pass
		
		assert inner.__acl__ == (None,)
	
	def test_acl_result_behaviour(self):
		assert bool(ACLResult(True, None)) is True
		assert bool(ACLResult(False, None)) is False
		assert bool(ACLResult(None, None)) is False


class TestBasicPredicateBehaviour(object):
	def test_bare_predicate_fails(self):
		with pytest.raises(NotImplementedError):
			Predicate()()
	
	def test_predicate_partial(self):
		predicate = Not.partial(always)
		assert predicate()() is False
	
	def test_always(self):
		assert always() is True
	
	def test_never(self):
		assert never() is False
	
	def test_not(self):
		assert Not(always)() is False
		assert Not(never)() is True
		
		with must_be_called(1) as nop:
			assert Not(nop)(27) is None


class TestFirstPredicate(object):
	def test_first_nop(self):
		with must_be_called(3) as nop:
			assert First(nop, nop, nop)('fnord') is None
	
	def test_first_truthy(self):
		assert First(always, always, always)() is True
		
		with must_be_called(2) as nop:
			assert First(nop, nop, always)() is True
		
		with must_not_be_called() as canary:
			assert First(always, canary, canary)() is True
	
	def test_first_falsy(self):
		assert First(never, never, never)() is False
		
		with must_be_called(2) as nop:
			assert First(nop, nop, never)() is False
		
		with must_not_be_called() as canary:
			assert First(never, canary, canary)() is False


class TestAllPredicate(object):
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


class TestAnyPredicate(object):
	def test_any_nop(self):
		with must_be_called(3) as nop:
			assert Any(nop, nop, nop)('fnord') is None
	
	def test_any_truthy(self):
		assert Any(always, always, always)() is True
		
		with must_not_be_called() as canary:
			assert Any(always, canary, canary)() is True
		
		with must_not_be_called() as canary:
			with must_be_called(1) as nop:
				assert Any(nop, always, canary)() is True
	
	def test_any_falsy(self):
		assert Any(never, never, never)() is False
		
		with must_be_called(2) as nop:
			assert Any(never, nop, nop)() is False
		
		with must_be_called(2) as nop:
			assert Any(nop, nop, never)() is False


class TestContextMatchPredicate(object):
	local_request = Request.blank('/', remote_addr='127.0.0.1')
	
	def test_bad_arguments(self):
		with pytest.raises(TypeError):
			ContextMatch(True, 'foo', 27, foo=27)
		
		with pytest.raises(TypeError):
			ContextMatch(True, 'foo')
		
		with pytest.raises(ValueError):
			ContextMatch('foo', 'bar', 27)
		
		with pytest.raises(ValueError):
			ContextMatch(True, 'foo', 27, default='bar')
	
	def test_admin_example_with_no_user(self, admin, context):
		assert admin(context) is None
	
	def test_admin_example_user_with_no_admin_field(self, admin, context):
		context.user = Context()
		assert admin(context) is None
	
	def test_admin_example_user_who_is_not_admin(self, admin, context):
		context.user = Context(admin=False)
		assert admin(context) is None
	
	def test_admin_example_user_who_is_admin(self, admin, context):
		context.user = Context(admin=True)
		assert admin(context) is True


class TestContextContainsPredicate(object):
	def test_reviewer_example_with_no_user(self, reviewer, context):
		assert reviewer(context) is None
	
	def test_reviewer_example_with_no_role_field(self, reviewer, context):
		context.user = Context()
		assert reviewer(context) is None
	
	def test_reviewer_example_without_role(self, reviewer, context):
		context.user = Context(role={'peasant'})
		assert reviewer(context) is None
	
	def test_reviewer_example_with_role(self, reviewer, context):
		context.user = Context(role={'reviewer'})
		assert reviewer(context) is True


class TestExtensionBehaviour(object):
	def do(self, controller, **data):
		app = Application(controller, extensions=[ACLExtension()])
		req = Request.blank('/')
		
		if data:
			req.content_type = 'application/json'
			if data:
				req.json = data
		
		return req.get_response(app).status_int
	
	def test_no_explicit_rules(self):
		assert self.do(MockController) == 200
	
	def test_explicit_intermediate_grant(self):
		assert self.do(Grant) == 200
	
	def test_early_grant(self):
		assert self.do(EarlyGrant) == 200
	
	def test_early_deny(self):
		assert self.do(EarlyDeny) == 403

