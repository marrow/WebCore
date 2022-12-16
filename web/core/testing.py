from webob import Request
from uri import URI, Bucket


class MockRequest:
	def __init__(self, verb='GET', endpoint=None, format='json', data=None, **kw):		
		self.url = URI("http://localhost:8080/") / (endpoint or '')
		self.verb = verb
		self.data = data
		self.format = format
		
		for k, v in kw.items():
			self.url.query.buckets.append(Bucket(k ,v))
	
	def __enter__(self):
		if self.verb == 'POST': 
			req = Request.blank(str(self.url) + '/', POST=str(self.data))
		else: req = Request.blank(str(self.url))
		
		return req
	
	def __exit__(self, exc_type, exc_value, traceback):
		pass
