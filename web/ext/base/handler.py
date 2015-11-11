# encoding: utf-8

import _io
import io
import types
import collections
from os.path import normpath, exists, isfile, getmtime, getsize, join as pathjoin
from mimetypes import guess_type
from time import mktime, gmtime
from datetime import datetime

from webob import Response
from web.core.compat import str, unicode


__all__ = ['serve', 'response', 'textual', 'generator', 'empty', 'wsgi']

log = __import__('logging').getLogger(__name__)



def kinds(*types):
	def decorator(fn):
		fn.types = types
		return fn
	
	return decorator


@kinds(io.TextIOBase, io.BufferedIOBase, io.RawIOBase, io.IOBase)
#@kinds(_io.TextIOWrapper, _io.StringIO, _io.FileIO, _io.BytesIO)
def serve(context, result):
	# To the "right" thing.
	# Seek to the end then tell to get length.
	# Check the config from the context to determine use of X-Sendfile.
	log.debug("%d:Processing file-like object.", id(context.request))
	
	request = context.request
	response = context.response = Response(
			conditional_response = True
		)
	
	modified = mktime(gmtime(getmtime(result.name)))
	
	response.last_modified = datetime.fromtimestamp(modified)
	response.cache_control = 'public'
	ct, ce = guess_type(result.name)
	if not ct: ct = 'application/octet-stream'
	response.content_type, response.content_encoding = ct, ce
	response.etag = unicode(modified)
	
	result.seek(0, 2)  # Seek to the end of the file.
	response.content_length = result.tell()
	
	result.seek(0)  # Seek to the start of the file.
	response.body_file = result
	
	return True


@kinds(Response)
def response(context, result):
	context.response = result
	return True


@kinds(str, unicode)
def textual(context, result):
	context.response.text = result
	return True


@kinds(types.GeneratorType)
def generator(context, result):
	context.response.encoding = 'utf8'
	context.response.app_iter = ((i.encode('utf8') if isinstance(i, unicode) else i) for i in result if i is not None)
	return True


@kinds(type(None))
def empty(context, result):
	context.response.length = 0
	context.response.body = None
	return True


@kinds(tuple)
def wsgi(context, result):
	if len(result) != 3 or not (isinstance(result[0], str) or isinstance(result[1], list)):
		return False
	
	r = context.response
	r.status = result[0]
	r.headers.clear()
	r.headers = dict(result[1])
	r.body = result[2]
	
	return True
