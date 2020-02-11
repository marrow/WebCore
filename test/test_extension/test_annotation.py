# encoding: utf-8

import pytest

from web.core.context import Context
from web.ext.annotation import AnnotationExtension


def endpoint(a: int, b: int) -> 'int':
	return a * b

class Endpoint:
	def endpoint(a: int, b: int):
		return a * b

def bare_endpoint(a, b):
	return a * b


def test_annotation_extension():
	ext = AnnotationExtension()
	ctx = Context()
	args = []
	kwargs = {'a': '27', 'b': '42'}
	
	ext.mutate(ctx, endpoint, args, kwargs)
	
	assert kwargs == {'a': 27, 'b': 42}


def test_annotation_bare():
	ext = AnnotationExtension()
	ctx = Context()
	args = []
	kwargs = {'a': '27', 'b': '42'}
	
	ext.mutate(ctx, bare_endpoint, args, kwargs)
	
	assert kwargs == {'a': '27', 'b': '42'}
	
	assert ext.transform(ctx, bare_endpoint, None) is None


def test_annotation_method():
	ext = AnnotationExtension()
	ctx = Context()
	args = []
	kwargs = {'a': '27', 'b': '42'}
	
	ext.mutate(ctx, Endpoint().endpoint, args, kwargs)
	
	assert kwargs == {'a': 27, 'b': 42}


def test_annotation_positional():
	ext = AnnotationExtension()
	ctx = Context()
	args = ['27', '42']
	kwargs = {}
	
	ext.mutate(ctx, endpoint, args, kwargs)
	
	assert args == [27, 42]
	assert kwargs == {}


def test_annotation_transformation():
	ext = AnnotationExtension()
	ctx = Context()
	
	result = ext.transform(ctx, endpoint, 1134)
	
	assert result == ('int', 1134)


def test_annotation_failure():
	ext = AnnotationExtension()
	ctx = Context()
	args = []
	kwargs = {'a': 'xyzzy'}
	
	with pytest.raises(ValueError):
		ext.mutate(ctx, endpoint, args, kwargs)
	
	try:
		ext.mutate(ctx, endpoint, args, kwargs)
	except ValueError as e:
		s = str(e)
		
		assert 'xyzzy' in s
		assert "argument 'a'" in s
