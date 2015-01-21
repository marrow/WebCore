# encoding: utf-8

import web.core

from unittest import TestCase
from webob import Request
from webob.cookies import Cookie


__all__ = ['PlainController', 'WebTestCase']



class PlainController(web.core.Controller):
    def __before__(self, *parts, **data):
        web.core.response.content_type = "text/plain"
        return super(PlainController, self).__before__(*parts, **data)


class WebTestCase(TestCase):
    def __init__(self, *args, **kw):
        self._cookies = dict()
        super(WebTestCase, self).__init__(*args, **kw)

    def _handle_cookies(self, resp):
        existing = resp.headers.getall('Set-Cookie')
        if not existing:
            return dict()

        cookies = Cookie()
        for header in existing:
            cookies.load(header)

        for key in cookies:
            self._cookies[key] = cookies[key].value

    def assertResponse(self, path, status='200 OK', content_type='text/plain', _method='GET', _environ=None, **kw):
        _environ = _environ or {}
        _environ.setdefault('REMOTE_ADDR', '127.0.0.1')

        #_environ.setdefault('HTTP_COOKIE', "; ".join((a + "=" + b) for a, b in self._cookies.iteritems()))

        request = Request.blank(path, environ=_environ)
        request.method = _method
        request.cookies.update(self._cookies)

        response = request.get_response(self.app)
        self._handle_cookies(response)

        self.assertEqual((response.status, response.content_type), (status, content_type))

        for i, j in kw.iteritems():
            self.assertEqual(getattr(response, i), j)

        return response

    def assertPostResponse(self, path, data={}, status='200 OK', content_type='text/plain', _environ=None, **kw):
        _environ = _environ or {}
        _environ.setdefault('REMOTE_ADDR', '127.0.0.1')
        request = Request.blank(path, environ=_environ)
        request.method = "POST"
        request.headers.setdefault('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
        for key in self._cookies:
            request.cookies[key] = self._cookies[key]
        request.POST.update(data)

        response = request.get_response(self.app)
        self._handle_cookies(response)

        self.assertEqual((response.status, response.content_type), (status, content_type))

        for i, j in kw.iteritems():
            self.assertEqual(getattr(response, i), j)

        return response
