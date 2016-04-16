# encoding: utf-8

from __future__ import unicode_literals

import pytest

from webob import Request
from web.core import Application

from crudlike import Root


def do(path):
	app = Application(Root)
	req = Request.blank(path)
	return req.get_response(app)


class TestCrudlikeRoot(object):
	def test_resolve_root(self):
		with pytest.raises(TypeError):
			do('/')
	
	def test_no_resolve_other(self):
		assert do('/foo').status_int == 404
	
	def test_no_resolve_private(self):
		assert do('/__class__').status_int == 404


class TestCrudlikeCollection(object):
	def test_resolve_user_collection(self):
		assert do('/user').text == "I'm all people."
	
	def test_resolve_specific_user(self):
		assert do('/user/GothAlice').text == "Hi, I'm GothAlice"
	
	def test_resolve_specific_user_action(self):
		assert do('/user/GothAlice/foo').text == "I'm also GothAlice"

