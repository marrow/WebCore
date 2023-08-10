from warnings import warn
from typing import Any, Optional, Mapping

from uri import URI, Bucket
from web.auth import authenticate, deauthenticate
from web.core import local
from webob import Request, Response
from webob.exc import HTTPOk



class MockRequest:
	"""Prepare a new, mocked request.
	
	Must be passed the current context and the path to an endpoint to execute.
	
	The `verb` defaults to "get". Any `data` passed in will be encoded as the request body. Additional keyword
	arguments are treated as query string parameters. These will be added to the existing set, they will not override
	existing values present in the base endpoint URI.
	"""
	
	__slots__ = ('url', 'verb', 'data', 'user')
	
	uri: URI
	verb: str
	data: Optional[Mapping]
	user: Any
	
	def __init__(self, verb='GET', endpoint='', data=None, user=None, **kw):
		self.uri = URI("http://localhost:8080/") / endpoint
		self.verb = verb
		self.data = data
		self.user = user
		
		for k, v in kw.items():
			self.uri.query.buckets.append(Bucket(k ,v))
	
	def __enter__(self):
		req = Request.blank(str(self.uri), POST=self.data, environ={'REQUEST_METHOD': self.verb})
		if self.user: req.environ['web.account'] = self.user
		return req


def validate(app, verb, path, data=None, user=None, expect=None):
	if expect is None: expect = HTTPOk
	location = None
	
	print(f"Issuing {verb} request to {path} as {user}, expecting: {expect}")
	
	with MockRequest(verb, path, user=user, **((data or {}) if verb == 'GET' else {'data': data})) as request:
		response = request.send(app)
	
	if isinstance(expect, tuple): expect, location = expect
	assert response.status_int == expect.code
	if location: assert response.location == 'http://localhost:8080' + location
	
	return response

