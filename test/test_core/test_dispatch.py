# encoding: utf-8

from unittest import TestCase

from inspect import isclass
from webob import Request
from web.core.context import Context
from web.core.dispatch import WebDispatchers


class DispatchBase(TestCase):
	def setUp(self):
		self._ctx = Context(
				request = Request.blank('/foo/bar'),
				extension = Context(signal=Context(dispatch=[])),
				dispatched = False,
				callback = False,
				events = [],
			)
		self.dispatch = self._ctx.dispatch = WebDispatchers(self._ctx)
		self._ctx.environ = self._ctx.request.environ


class TestDispatchProtocol(DispatchBase):
	def wire(self, callback):
		self._ctx.extension = Context(signal=Context(dispatch=[callback]))
	
	def mock_dispatcher(self, context, handler, path):
		assert context is self._ctx
		context.dispatched = True
		yield path, handler, True
	
	def mock_no_dispatch(self, context, handler, path):
		assert context is self._ctx
		context.dispatched = True
		yield None, handler, False
	
	#def mock_dispatcher(self, context, handler, path):
	#	assert context is self._ctx
	#	context.dispatched = True
	#	yield path, handler, True
	
	def mock_explody_dispatcher(self, context, handler, path):
		assert context is self._ctx
		context.dispatched = True
		raise LookupError()
	
	def basic_endpoint(self, dispatcher):
		def closure(context): pass
		closure.__dispatch__ = dispatcher
		return closure
	
	def callback(self, context, consumed, handler, is_endpoint):
		context.callback = True
	
	def test_basic_mock(self):
		endpoint = self.basic_endpoint(self.mock_dispatcher)
		is_endpoint, handler = self.dispatch(self._ctx, endpoint, self._ctx.request.path)
		assert is_endpoint
		assert handler is endpoint
		assert self._ctx.dispatched
	
	def test_dispatch_failure(self):
		endpoint = self.basic_endpoint(self.mock_explody_dispatcher)
		is_endpoint, handler = self.dispatch(self._ctx, endpoint, self._ctx.request.path)
		assert not is_endpoint
		assert handler is None
		assert self._ctx.dispatched
	
	def test_dispatch_going_nowhere(self):
		endpoint = self.basic_endpoint(self.mock_no_dispatch)
		is_endpoint, handler = self.dispatch(self._ctx, endpoint, self._ctx.request.path)
		assert not is_endpoint
		assert handler is None
		assert self._ctx.dispatched



class TestDispatchPlugins(DispatchBase):
	def test_existing_callable_lookup(self):
		def closure(): pass
		
		assert self.dispatch[closure] is closure
	
	def test_class_instantiation(self):
		class Closure(object): pass
		result = self.dispatch[Closure]
		
		assert isinstance(result, Closure)
	
	def test_named_cache(self):
		assert 'object' in self.dispatch.named  # TODO: skip test if missing
		assert isclass(self.dispatch.named['object'])
		
		dispatcher = self.dispatch['object']
		
		assert 'Object' in dispatcher.__class__.__name__
		assert 'object' in self.dispatch.named
		assert self.dispatch.named['object'] is dispatcher

