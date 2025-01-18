from warnings import warn
from typing import Any, Optional, Mapping

from uri import URI, Bucket
from web.auth import authenticate, deauthenticate
from web.core import local
from webob import Request, Response
from webob.exc import HTTPException, HTTPOk


''' WIP
from pytest import fixture


@fixture(scope='session', autouse=True)
def testing_context(application):
	"""Provide and manage the TestingContext Pytest must execute within.
	
	Your own test suite must define a fixture named `application`, which will be utilized by this fixture to populate
	the context and signal any configured extensions.
	"""
	
	original = local.context
	signals = original.extension.signal
	
	# Prepare a TestingContext using a blank request.
	request = Request.blank('/')
	context = app.RequestContext(environ=request.environ)._promote('TestingContext')
	
	# notify suite began
	
	yield context
	
	# notify suite finished
	
	for ext in signals.stop: ext(original)
	
	local.context = original


@fixture(scope='function', autouse=True)
def test_context(testing_context):
	for ext in signals.pre: ext(testing_context)
	for ext in signals.test: ext(testing_context)
	
	yield context
	
	for ext in signals.after: ext(testing_context)
	for ext in signals.done: ext(testing_context)
'''


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
	
	def __init__(self, verb:str='GET', path:str='', data:Optional[Mapping]=None, user:Optional[str]=None, /, **kw):
		"""Construct the components necessary to request a given endpoint directly from a WSGI application.
		
		Form-encoded body data is specified by way of the `data` argument; keyword arguments are added to the endpoint
		URI as query string arguments. Active user mocking exposes a `web.account` WSGI environment variable.
		"""
		
		self.uri = URI("http://localhost/") / path
		self.verb = verb
		self.data = data
		self.user = user
		
		for k, v in kw.items():
			self.uri.query.buckets.append(Bucket(k ,v))
	
	def __enter__(self):
		"""Populate and hand back a populated mock WebOb Request object, ready to be invoked."""
		req = Request.blank(str(self.uri), POST=self.data, environ={'REQUEST_METHOD': self.verb})
		if self.user: req.environ['web.account'] = self.user
		return req
	
	@classmethod
	def send(MockRequest, app:WSGI, verb:str='GET', path:str='', data:Optional[Mapping]=None, user:Optional[str]=None,
				expect:Optional[HTTPException]=None) -> Response:
		"""Populate, then invoke a populated WebOb Request instance against the given application.
		
		This returns the resulting WebOb Response instance.
		"""
		
		if expect is None: expect = HTTPOk
		location = None
		
		with MockRequest(verb, path, user=user, **((data or {}) if verb == 'GET' else {'data': data})) as request:
			response = request.send(app)
		
		if isinstance(expect, tuple): expect, location = expect
		assert response.status_int == expect.code
		if location: assert response.location == 'http://localhost:8080' + location
		
		return response

