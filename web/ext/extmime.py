# encoding: utf-8

from mimetypes import guess_type


class AcceptFilenameExtension(object):
	"""This pre-processes the incoming request URL, using the mimetype associated with the filename extension as the
	Accept header."""
	
	first = True
	
	needs = {'request'}
	provides = {'request.accept'}
	
	def prepare(self, context):
		encoding, compression = guess_type(context.environ['PATH_INFO'])
		
		if encoding:
			context.request.accept = encoding + context.request.accept
