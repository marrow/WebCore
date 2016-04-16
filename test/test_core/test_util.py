# encoding: utf-8

from web.core.context import Context
from web.core.util import lazy

def mock_lazy_value(context):
	context.ran = True
	context.count += 1
	return 42


def test_lazy_context_value():
	Ctx = Context(sample=lazy(mock_lazy_value, 'sample'))._promote('MockContext', False)
	ctx = Ctx(count=0, ran=False)
	
	assert isinstance(Ctx.sample, lazy)
	assert 'sample' not in ctx.__dict__
	assert not ctx.ran
	assert ctx.count == 0
	assert ctx.sample == 42
	assert 'sample' in ctx.__dict__
	assert ctx.sample == 42
	assert ctx.count == 1

