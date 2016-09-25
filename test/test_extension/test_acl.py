# encoding: utf-8

from __future__ import unicode_literals

import pytest
from contextlib import contextmanager
from webob import Request

from web.core.application import Application
from web.core.context import Context
from web.ext.serialize import SerializationExtension
from web.ext.acl import when, ACLResult, ACL, ACLExtension
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
	
	def test(self):
		return None
	
	def allowed(self):
		class secret(dict):
			__acl__ = [always]
		return secret(value=27)
	
	def forbidden(self):
		class secret(dict):
			__acl__ = [never]
		return secret(value=27)


@when(always)
class Grant(MockController):
	pass


@when(always)
class EarlyGrant(MockController):
	@when(never)
	def test(self):
		return None


@when(never)
class EarlyDeny(MockController):
	@when(always)
	def test(self):
		return None


@when(never)
class Nuke(MockController):
	@when(inherit=False)
	def test(self):
		return None


# # Tests


class TestPredicateHelpers(object):
	def test_when_decorator(self):
		@when(None)
		def inner(): pass
		
		assert inner.__acl__ == (None,)
		
		with pytest.raises(TypeError):
			when(foo=27)
	
	def test_acl_result_behaviour(self):
		assert bool(ACLResult(True, None)) is True
		assert bool(ACLResult(False, None)) is False
		assert bool(ACLResult(None, None)) is False
	
	def test_acl_invalid_construction(self):
		with pytest.raises(TypeError):
			ACL(foo=27)
	
	def test_acl_repr(self):
		acl = ACL(27, policy=(42,))
		assert repr(acl) == '[(None, 27, None), (None, 42, None)]'
	
	def test_acl_skip(self):
		with must_be_called(1) as nop:
			acl = ACL(nop, always)
			assert acl.is_authorized.result is True
	
	def test_acl_fallthrough(self):
		with must_be_called(1) as nop:
			acl = ACL(nop)
			assert acl.is_authorized.result is None


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
	def do(self, controller, path='/test', **config):
		app = Application(controller, extensions=[ACLExtension(**config), SerializationExtension()])
		req = Request.blank(path)
		resp = req.get_response(app)
		return resp.json if resp.status_int == 200 and resp.body else resp.status_int
	
	def test_unknown_kwarg(self):
		with pytest.raises(TypeError):
			ACLExtension(foo=27)
	
	def test_chained_policy(self):
		ext = ACLExtension(always, policy=[never])
		assert ext.policy[0] is always
		assert ext.policy[1] is never
	
	def test_defaults(self):
		assert self.do(MockController) == 200
		assert self.do(Grant) == 200
		assert self.do(EarlyGrant) == 200
		assert self.do(EarlyDeny) == 403
	
	def test_existing_policy(self):
		assert self.do(MockController, policy=[always]) == 200
		assert self.do(Grant, policy=[always]) == 200
		assert self.do(EarlyGrant, policy=[always]) == 200
		assert self.do(EarlyDeny, policy=[always]) == 403
	
	def test_default_policy(self):
		assert self.do(MockController, default=never) == 403
		assert self.do(Grant, default=never) == 200
		assert self.do(EarlyGrant, default=never) == 200
		assert self.do(EarlyDeny, default=never) == 403
	
	def test_empty_policy(self):
		assert Nuke.test.__acl_inherit__ is False
		assert self.do(Nuke) == 200
	
	def test_return_value_success(self):
		assert self.do(MockController, '/allowed') == {'value': 27}
	
	def test_return_value_failure(self):
		assert self.do(MockController, '/forbidden') == 403

