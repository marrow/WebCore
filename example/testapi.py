"""An example providing a broad range of potentially useful example API endpoints."""

from web.core import Application
from web.ext.annotation import AnnotationExtension
from web.ext.serialize import SerializationExtension

from web.dispatch.resource import Resource


class IP(Resource):
	def get(self):
		return {'ip': self._ctx.request.client_addr}


class Headers(object):
	def __init__(self, context, container=None):
		self._ctx = context
	
	def __call__(self):
		return dict(self._ctx.request.headers)


class Now(Resource):
	def get(self, component=None):
		pass




