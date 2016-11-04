# encoding: utf-8

import time
import pytest

from webob import Request
from web.core import Application
from web.core.context import Context
from web.ext.analytics import AnalyticsExtension


def endpoint(context):
	time.sleep(0.1)
	return "Hi."


sample = Application(endpoint, extensions=[AnalyticsExtension()])


def test_analytics_extension():
	ctx = Context(response=Context(headers=dict()))
	ext = AnalyticsExtension()
	
	assert not hasattr(ctx, '_start_time')
	ext.prepare(ctx)
	
	assert hasattr(ctx, '_start_time')
	ext.before(ctx)
	time.sleep(0.1)
	
	ext.after(ctx)
	assert 100 <= float(ctx.response.headers['X-Generation-Time']) <= 200


def test_analytics_extension_in_context():
	try:
		__import__('web.dispatch.object')
	except ImportError:
		pytest.skip("web.dispatch.object not installed")
	
	resp = Request.blank('/').get_response(sample)
	assert 100 <= float(resp.headers['X-Generation-Time']) <= 200

