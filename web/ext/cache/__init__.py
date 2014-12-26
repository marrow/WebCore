# encoding: utf-8

from __future__ import unicode_literals, print_function

try:
	from marrow.cache import Cache
except ImportError:
	print("Unable to find the marrow.cache package. To correct this, run: pip install marrow.cache")
	raise


class CacheExtension(object):
	provides = ["cache"]
	
	def start(self, context):
		"""Executed during application startup just after binding the server."""
		
		context.cache = Cache
