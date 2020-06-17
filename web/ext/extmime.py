from mimetypes import guess_type

from ..core.typing import Context, Tags, check_argument_types


class AcceptFilenameExtension:
	"""Processes the request path, using the mimetype associated with the filename extension as the Accept header.
	
	This is predominantly to permit less capable HTTP user agents not capable of independently assigning an Accept
	header, such as typical browser user-agents with simple anchor references. This does not replace the existing
	header, if present, it prepends any detected type to the list.
	"""
	
	first: bool = True
	needs: Tags = {'request'}
	provides: Tags = {'request.accept'}
	
	def prepare(self, context:Context) -> None:
		assert check_argument_types()
		
		encoding, _ = guess_type(context.environ['PATH_INFO'])
		
		if encoding:
			context.request.accept = encoding + context.request.accept
