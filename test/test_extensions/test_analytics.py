# encoding: utf-8

import time

from web.core.context import Context
from web.ext.analytics import AnalyticsExtension


def test_analytics_extension():
	ctx = Context(response=Context(headers=dict()))
	ext = AnalyticsExtension()
	
	assert not hasattr(ctx, '_start_time')
	ext.prepare(ctx)
	
	assert hasattr(ctx, '_start_time')
	ext.before(ctx)
	time.sleep(0.1)
	
	ext.after(ctx)
	assert 0.1 <= float(ctx.response.headers['X-Generation-Time']) <= 0.2

