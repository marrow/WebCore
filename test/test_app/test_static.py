# encoding: utf-8

from __future__ import unicode_literals

import os.path
import pytest

from webob.exc import HTTPForbidden, HTTPNotFound
from web.app.static import static


HERE = os.path.dirname(__file__)

class Sample(object):
	ep = static(HERE)
	epm = static(HERE, dict(html='mako'))
	dev = static('/dev')

sample = Sample()


def test_base_path_policy():
	with pytest.raises(HTTPForbidden):
		sample.ep(None, '..', 'foo')
	
	with pytest.raises(HTTPForbidden):
		sample.ep(None, '/', 'foo')


def test_non_extant():
	with pytest.raises(HTTPNotFound):
		sample.ep(None, 'noex')


def test_non_file():
	with pytest.raises(HTTPForbidden):
		sample.ep(None)


def test_mapping():
	template, data = sample.epm(None, 'foo.html')
	
	assert data == dict()
	assert template == 'mako:' + os.path.join(HERE, 'foo.html')


def test_file():
	fh = sample.ep(None, 'foo.html')
	assert fh.read().strip() == b'html'
	fh.close()
	
	fh = sample.ep(None, 'foo.txt')
	assert fh.read().strip() == b'text'
	fh.close()

