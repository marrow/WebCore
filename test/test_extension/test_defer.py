# encoding: utf-8

from concurrent.futures import ThreadPoolExecutor
from webob import Request

from web.core import Application
from web.ext.defer import DeferralExtension, DeferredExecutor


sentinel = object()


results = []


def deferred(a, b):
	global results
	results.append("called")
	return a * b


def double(a):
	global results
	return a * 2


def resulting(receipt):
	global results
	results.append("returned")
	results.append(receipt.result())


class Root(object):
	def __init__(self, ctx):
		self.ctx = ctx
	
	def __call__(self):
		receipt = self.ctx.defer.submit(deferred, 2, 4)
		receipt.add_done_callback(resulting)
		return repr(receipt)
	
	def blank(self):
		return "nope"
	
	def deferred_body(self):
		def inner():
			return "yup"
		
		return self.ctx.defer.submit(inner)
	
	def isa(self):
		return type(self.ctx.defer).__name__ + '\n' + type(self.ctx.executor).__name__
	
	def prop(self, p, invoke=False, *args, **kw):
		receipt = self.ctx.defer.submit(deferred, 2, 4)
		receipt.add_done_callback(resulting)
		
		if invoke:
			receipt._schedule()
		
		attr = getattr(receipt, p)
		if callable(attr):
			result = attr(*args, **kw)
			return repr(attr) + "\n" + repr(result)
		return repr(attr)
	
	def map(self):
		parts = [1, 2, 4, 8]
		
		iterator = self.ctx.defer.map(double, parts)
		return '\n'.join(str(i) for i in iterator)


class TestDeferralExtension(object):
	app = Application(Root, extensions=[DeferralExtension()])
	
	def dtest_use(self):
		req = Request.blank('/')
		status, headers, body_iter = req.call_application(self.app)
	
	def test_non_use(self):
		req = Request.blank('/blank')
		status, headers, body_iter = req.call_application(self.app)
	
	def test_preparation(self):
		app = Application(Root, extensions=[DeferralExtension()])
		ctx = app._Application__context  # "private" attribute
		
		assert 'executor' in ctx
		assert isinstance(ctx.executor, ThreadPoolExecutor)
		
		ctx = ctx._promote('RequestContext')
		
		assert 'defer' in ctx
		assert isinstance(ctx.defer, DeferredExecutor)
	
	def test_submission_and_repr(self):
		req = Request.blank('/')
		status, headers, body_iter = req.call_application(self.app)
		body = b''.join(body_iter).decode('utf8')
		
		# DeferredFuture(<function deferred at 0xYYYYYYYY>, *(2, 4), **{}, callbacks=1)
		
		assert body.startswith('DeferredFuture(')
		assert 'function deferred' in body
		assert '*(2, 4)' in body
		assert '**{}' in body
		assert body.endswith(', callbacks=1)')
		
		assert len(results) == 3
		assert results == ['called', 'returned', 8]
		del results[:]
	
	def test_attributes(self):
		def attr(name, executed=True, immediate=False):
			req = Request.blank('/prop/' + name + ("?invoke=True" if immediate else ""))
			status, headers, body_iter = req.call_application(self.app)
			result = b''.join(body_iter).decode('utf8').partition('\n')[::2]
			# Body must complete iteration before we do any tests against the job...
			
			if executed and name != 'cancel':
				assert len(results) == 3
				assert results == ['called', 'returned', 8]
				del results[:]
			else:
				assert len(results) == 0
			
			return result
		
		assert attr('cancel', False)[1] == 'True'
		assert attr('cancel', True)[1] == 'True'
		
		assert attr('cancelled')[1] == 'False'
		assert attr('running')[1] == 'False'
		assert attr('done')[1] == 'False'
		
		assert attr('result')[1] == '8'
		assert attr('exception')[1] == 'None'
		
		assert attr('_internal')[0] == 'None'
		assert attr('_internal', immediate=True)[0] != 'None'
	
	def test_map(self):
		req = Request.blank('/map')
		status, headers, body_iter = req.call_application(self.app)
		body = b''.join(body_iter).decode('utf8')
		results = [int(i) for i in body.split()]
		
		assert results == [2, 4, 8, 16]
	
	def test_context(self):
		req = Request.blank('/isa')
		status, headers, body_iter = req.call_application(self.app)
		body = b''.join(body_iter).decode('utf8')
		defer, _, executor = body.partition('\n')
		
		assert defer == 'DeferredExecutor'
		assert executor == 'ThreadPoolExecutor'
	
	def test_deferred_body(self):
		req = Request.blank('/deferred_body')
		status, headers, body_iter = req.call_application(self.app)
		body = b''.join(body_iter).decode('utf8')
		
		assert body == 'yup'





'''


def test_deferred_future():
	"""
	test task.cancel()
	test task.cancelled()
	test task.running()
	test task.done()
	test task.result()
	test task.exception()
	test task.add_done_callback() with Executor
	test task.set_running_or_notify_cancel()
	test task.schedule() with Executor
	"""
	pass


def test_deferred_executor():
	executor = ThreadPoolExecutor()
	
	deferred_executor = DeferredExecutor(executor)
	
	future = deferred_executor.submit(sentinel)
	assert future is not None
	deferred_executor.shutdown()
	assert future.running() is True
	
	future = deferred_executor.submit(sentinel)
	deferred_executor.shutdown(wait=False)
	assert future.running() is False
	
	deferred_executor._schedule_one(future)
	assert future.running() is True


def test_defer_extension_executor():
	ctx = Context()
	ext = DeferralExtension(Executor=ThreadPoolExecutor)
	
	ext.start(ctx)
	assert hasattr(ctx, 'executor')
	assert isinstance(ctx.executor, ThreadPoolExecutor)
	ext.stop(ctx)


def test_defer_extension_deferred_executor():
	ctx = Context()
	ext = DeferralExtension(Executor=ThreadPoolExecutor)
	ext.start(ctx)
	
	assert hasattr(ctx, 'defer')
	#assert isinstance(ctx.deferred_executor, lazy)
	
	rctx = ctx._promote('RequestContext')
	assert 'defer' not in rctx.__dict__
	assert hasattr(rctx, 'executor')
	
	# done correctly executes deferred futures
	future = rctx.defer.submit(sentinel)
	assert 'defer' in rctx.__dict__ and isinstance(rctx.defer, DeferredExecutor)
	ext.done(rctx)
	assert future.running() is True
	
	# Test that deferred executor is never lazy loaded if not ccessed
	rctx = ctx._promote('RequestContext')
	ext.done(rctx)
	assert 'defer' not in rctx.__dict__
	
	ext.stop(ctx)
	assert ctx.executor._shutdown is True

'''

if __name__ == '__main__':
	TestDeferralExtension.app.serve('wsgiref')
