# encoding: utf-8

import pytest

from web.core.context import Context, ContextGroup


class Thing(object):
	def __init__(self):
		self.__name__ = None


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
	
	thing = group.foo = Thing()
	assert repr(group) == "ContextGroup(foo)"
	assert len(group) == 1
	assert list(group) == ['foo']
	assert group.foo is thing
	
	thing = group['bar'] = Thing()
	assert repr(group) == "ContextGroup(bar, foo)"
	assert len(group) == 2
	assert set(group) == {'foo', 'bar'}
	assert group['bar'] is thing
	
	assert 'foo' in group
	del group.foo
	assert len(group) == 1
	assert set(group) == {'bar'}
	
	del group['bar']
	assert len(group) == 0


def test_context_group_initial_arguments():
	group = ContextGroup(foo=Thing(), bar=Thing())
	assert repr(group) == "ContextGroup(bar, foo)"
	assert len(group) == 2
	assert set(group) == {'foo', 'bar'}


def test_context_group_default():
	inner = Context()
	group = ContextGroup(default=inner)
	
	thing = inner.foo = Thing()
	assert inner.foo is thing
	assert group.foo is thing
	del group.foo
	
	assert 'foo' not in inner, list(inner)
	assert 'foo' not in group, 'foo remains in group'

