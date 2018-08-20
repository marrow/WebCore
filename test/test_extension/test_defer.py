# encoding: utf-8

from concurrent.futures import ThreadPoolExecutor

from web.core.context import Context
from web.core.util import lazy
from web.ext.defer import DeferralExtension, DeferredExecutor


def test_deferred_future():
	"""
	test task.cancel()
	test task.cancelled()
	test task.running()
	test task.done()
	test task.result()
	test task.exception()
	test task.add_done_callback() with MockExecutor
	test task.set_running_or_notify_cancel()
	test task.schedule() with MockExecutor
	"""
	pass


def test_deferred_executor():
	executor = MockExecutor()
	
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
	ext = DeferralExtension(Executor=MockExecutor)
	
	ext.start(ctx)
	assert hasattr(ctx, 'executor')
	assert isinstance(ctx.executor, MockExecutor)
	ext.stop(ctx)


def test_defer_extension_deferred_executor():
	ctx = Context()
	ext = DeferralExtension(Executor=MockExecutor)
	ext.start(ctx)
	
	assert hasattr(ctx, 'deferred_executor')
	assert isinstance(ctx.deferred_executor, lazy)
	
	rctx = ctx._promote('RequestContext')
	assert 'deferred_executor' not in rctx.__dict__
	assert hasattr(rctx, 'executor')
	
	# done correctly executes deferred futures
	future = rctx.deferred_executor.submit(sentinel)
	assert 'deferred_executor' in rctx.__dict__ and isinstance(rctx.deferred_executor, DeferredExecutor)
	ext.done(rctx)
	assert future.running() is True
	
	# Test that deferred_executor is never lazy loaded if not ccessed
	rctx = ctx._promote('RequestContext')
	ext.done(rctx)
	assert 'deferred_executor' not in rctx.__dict__
	
	ext.stop(ctx)
	assert ctx.executor._shutdown is True
