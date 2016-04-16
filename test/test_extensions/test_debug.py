# encoding: utf-8

import pytest

from webob import Request
from webob.exc import HTTPNotFound
from web.core.context import Context
from web.ext.debug import Console, DebugExtension


def mock_app(environ, start_response):
	1/0


def test_debug_extension_console():
	ext = DebugExtension()
	req = Request.blank('/__console__')
	ctx = Context()
	app = ext(ctx, mock_app)
	
	response = req.get_response(app)
	
	assert 'CONSOLE_MODE = true' in response.text


def test_debug_extension_catches():
	ext = DebugExtension()
	req = Request.blank('/')
	ctx = Context()
	app = ext(ctx, mock_app)
	
	response = req.get_response(app)
	
	assert 'CONSOLE_MODE = false' in response.text
	assert 'by zero' in response.text


def test_inline_console():
	ctx = Context()
	ctx.request = Request.blank('/')
	ext = DebugExtension()
	ext(ctx, mock_app)
	
	con = Console(ctx)
	
	result = con()
	assert 'CONSOLE_MODE = true' in result.text



def test_inline_console_disallowed():
	ctx = Context()
	ctx.request = Request.blank('/')
	con = Console(ctx)
	
	with pytest.raises(HTTPNotFound):
		con()

