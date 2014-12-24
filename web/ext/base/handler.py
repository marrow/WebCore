# encoding: utf-8

import types
import collections

from webob import Response
#from marrow.wsgi.objects import Response
from marrow.util.compat import binary, unicode


__all__ = ['response', 'textual', 'empty', 'wsgi']



def kinds(*types):
	def decorator(fn):
		fn.types = types
		return fn
	
	return decorator


@kinds(Response)
def response(context, result):
	context.response = result
	return True


@kinds(binary, unicode)
def textual(context, result):
	context.response.text = result
	return True


#@kinds(types.GeneratorType, collections.Iterable)
#def primary(context, result):
#	if isinstance(result, (tuple, dict)):
#		return False
#	
#	context.response.body = result
#	return True


@kinds(type(None))
def empty(context, result):
	context.response.length = 0
	context.response.body = None
	return True


@kinds(tuple)
def wsgi(context, result):
	if len(result) != 3 or not (isinstance(result[0], binary) or isinstance(result[1], list)):
		return False
	
	r = context.response
	r.status = result[0]
	r.headers.clear()
	r.headers = dict(result[1])
	r.body = result[2]
	
	return True

	# ds(file)
	# serve(context, result):
	# # To the "right" thing.
	# # Seek to the end then tell to get length.
	# # Check the config from the context to determine use of X-Sendfile.
	# context.response.body = result
	# return True
