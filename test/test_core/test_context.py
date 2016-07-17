# encoding: utf-8

import pytest

from web.core.context import Context, ContextGroup


def test_basic_context_operations():
	sample = Context(foo=1, bar=2, _baz=3)
	
	assert sorted(sample) == ['bar', 'foo']
	assert len(sample) == 2
	assert sample['foo'] == 1
	
	del sample['bar']
	
	with pytest.raises(KeyError):
		sample['bar']
	
	with pytest.raises(KeyError):
		del sample['bar']


def test_context_group_basics():
	group = ContextGroup()
	assert repr(group) == "ContextGroup()"
	assert len(group) == 0
	assert list(group) == []


