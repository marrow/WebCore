# encoding: utf-8

import web
from web.core import local
from web.core.context import Context
from web.ext.local import ThreadLocalExtension


def test_existing_thread_local_extension():
	ctx = Context()
	ext = ThreadLocalExtension()
	
	assert not hasattr(local, 'context')
	ext.start(ctx)
	
	assert local.context is ctx
	
	rctx = ctx._promote('RequestContext')
	ext.prepare(rctx)
	
	assert local.context is rctx
	
	ext.after(rctx)
	assert not hasattr(local, 'context')
	
	ext.stop(ctx)


def test_new_thread_local_extension():
	ctx = Context()
	ext = ThreadLocalExtension('web:local')
	
	assert not hasattr(web, 'local')
	
	ext.start(ctx)
	
	local = web.local
	
	assert local.context is ctx
	
	rctx = ctx._promote('RequestContext')
	ext.prepare(rctx)
	
	assert local.context is rctx
	
	ext.after(rctx)
	assert not hasattr(local, 'context')
	
	ext.stop(ctx)
	
	assert not hasattr(web, 'local')

