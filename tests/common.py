# encoding: utf-8

from unittest import TestCase
import web.core
from webob import Request


__all__ = ['PlainController', 'WebTestCase']



class PlainController(web.core.Controller):
    def __before__(self, *parts, **data):
        web.core.response.content_type = "text/plain"
        return super(PlainController, self).__before__(*parts, **data)


class WebTestCase(TestCase):
    def assertResponse(self, path, status='200 OK', content_type='text/plain', _method='get', **kw):
        request = Request.blank(path, environ=dict(REMOTE_ADDR='127.0.0.1'))
        request.method = _method
        
        response = request.get_response(self.app)
        
        self.assertEqual((response.status, response.content_type), (status, content_type))
        
        for i, j in kw.iteritems():
            self.assertEqual(getattr(response, i), j)
        
        return response
    
    def assertPostResponse(self, path, data={}, status='200 OK', content_type='text/plain', **kw):
        request = Request.blank(path)
        
        request.method = "POST"
        request.POST.update(data)
        
        response = request.get_response(self.app)
        
        self.assertEqual((response.status, response.content_type), (status, content_type))
        
        for i, j in kw.iteritems():
            self.assertEqual(getattr(response, i), j)
        
        return response
