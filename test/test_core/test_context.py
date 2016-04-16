# encoding: utf-8

import pytest

from web.core.context import Context


def test_basic_operations():
	sample = Context(foo=1, bar=2, _baz=3)
	
	assert sorted(sample) == ['bar', 'foo']
	assert len(sample) == 2
	assert sample['foo'] == 1
	
	del sample['bar']
	
	with pytest.raises(KeyError):
		sample['bar']
	
	with pytest.raises(KeyError):
		del sample['bar']



