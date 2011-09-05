# encoding: utf-8

import xmlrpclib

from webob import Request

from web.core import Application
from web.rpc.xml import XMLRPCController
from common import WebTestCase


test_config = {'debug': False, 'web.widgets': False, 'web.compress': False, 'web.static': False}


class RootController(XMLRPCController):
    __max_body_length__ = 1024

    def test(self):
        return "ok"

    def add(self, a, b):
        return a + b

    def error(self):
        1 / 0

    def bad(self):
        return None, object()

    def __before__(self, *args):
        self.args = args
        return args

    def __after__(self, result, *args):
        self.result = result
        return result


class TestXMLRPC(WebTestCase):
    root = RootController()
    app = Application.factory(root=root, **test_config)

    def assertRPCResponse(self, method, params=[], path='/', status='200 OK', content_type='text/xml', **kw):
        request = Request.blank(path, method="POST")
        request.body = xmlrpclib.dumps(tuple(params), method)

        response = request.get_response(self.app)

        self.assertEqual((response.status, response.content_type), (status, content_type))

        for i, j in kw.iteritems():
            self.assertEqual(getattr(response, i), j)

        data = None

        try:
            data = xmlrpclib.loads(response.body)
        except Exception, e:
            return response, e

        return response, data

    def test_basic(self):
        response, data = self.assertRPCResponse('test')
        self.assertEquals(data, (('ok',), None))

    def test_bad_method(self):
        response, data = self.assertRPCResponse('add')
        self.assertEquals(repr(data), "<Fault -32602: 'Invalid parameters to method.'>")

    def test_good_method(self):
        response, data = self.assertRPCResponse('add', [27, 42])
        self.assertEquals(data, ((69,), None))

    def test_internal_error(self):
        response, data = self.assertRPCResponse('error')
        self.assertEquals(repr(data), "<Fault -32500: 'Application error.'>")

    def test_bad_response(self):
        response, data = self.assertRPCResponse('bad')
        self.assertEquals(repr(data), "<Fault -32500: 'Application error.'>")

    def test_private(self):
        response, data = self.assertRPCResponse('_add')
        self.assertEquals(repr(data), "<Fault -32601: 'Requested method not found.'>")

    def test_bad_input(self):
        response, data = self.assertRPCResponse('add', [2, 4, 6])
        self.assertEquals(repr(data), "<Fault -32602: 'Invalid parameters to method.'>")

    def test_empty_request(self):
        request = Request.blank('/', method="POST", body="")
        response = request.get_response(self.app)
        self.assertEqual((response.status, response.content_type), ('411 Length Required', "text/plain"))

    def test_large_request(self):
        request = Request.blank('/', method="POST", body=" " * 1026)
        response = request.get_response(self.app)
        self.assertEqual((response.status, response.content_type), ('413 Request Entity Too Large', "text/plain"))

    def test_bad_xml_input(self):
        request = Request.blank('/', method="POST", body="<foo")
        response = request.get_response(self.app)

        with self.assertRaises(xmlrpclib.Fault):
            try:
                data = xmlrpclib.loads(response.body)
            except Exception, e:
                raise

        self.assertEquals(repr(e), "<Fault -32700: 'Not well formed.'>")

    def test_before(self):
        response, data = self.assertRPCResponse('add', [2, 4])
        self.assertEquals(self.root.args, (2, 4))

    def test_after(self):
        response, data = self.assertRPCResponse('add', [2, 4])
        self.assertEquals(self.root.result, 6)
