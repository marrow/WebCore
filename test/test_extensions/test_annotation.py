# encoding: utf-8

import pytest

from web.core.compat import py3
from web.core.context import Context


if not py3:
	pytest.skip("Python 3 required for annotation support.")
	raise ImportError("Python 3 only.")


from web.ext.annotation import AnnotationExtension

endpoint = None  # Correct mistaken linter.

# This trick hides the syntax error from Python 2.
exec("def endpoint(a: int, b: int) -> 'int': return a * b")


def bare_endpoint(a, b): return a * b


Endpoint = None  # Correct mistaken linter.

exec("class Endpoint:\n\tdef endpoint(a: int, b: int): return a * b")


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

