# encoding: utf-8

import pyamf
import pyamf.remoting

from webob import Request

from web.core import Application
from web.rpc.amf import AMFController
from common import WebTestCase


test_config = {'debug': False, 'web.widgets': False, 'web.compress': False, 'web.static': False}


class RootController(AMFController):
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


class TestAMFRPC(WebTestCase):
    root = RootController()
    app = Application.factory(root=root, **test_config)

    def assertRPCResponse(self, method, params=[], path='/', status='200 OK', content_type='application/x-amf', **kw):
        request = Request.blank(path, method="POST")
        request.content_type = 'application/x-amf'

        envelope = pyamf.remoting.Envelope(pyamf.AMF0)
        envelope['0'] = pyamf.remoting.Request(method, tuple(params))

        request.body = pyamf.remoting.encode(envelope).getvalue()

        response = request.get_response(self.app)

        if response.status_int == 200:
            envelope = pyamf.remoting.decode(response.body)
            data = envelope['0']
        else:
            data = None

        self.assertEqual((response.status, response.content_type), (status, content_type))

        for i, j in kw.iteritems():
            self.assertEqual(getattr(response, i), j)

        return response, data

    def test_basic(self):
        response, data = self.assertRPCResponse('test')
        self.assertEquals(data.body, 'ok')

    def test_bad_method(self):
        response, data = self.assertRPCResponse('add')
        self.assertEquals(data.body.code, "TypeError")
        self.assertEquals(data.body.description, "add() takes exactly 3 arguments (1 given)")

    def test_good_method(self):
        response, data = self.assertRPCResponse('add', [27, 42])
        self.assertEquals(data.body, 69)

    def test_internal_error(self):
        response, data = self.assertRPCResponse('error')
        self.assertEquals(data.body.code, "ZeroDivisionError")

    # TODO: Need to determine correct behaviour here.
    #       Currently will result in a 500 Internal Server Error in production.
    # def test_bad_response(self):
    #     response, data = self.assertRPCResponse('bad')
    #     self.assertEquals(data, "")

    def test_private(self):
        response, data = self.assertRPCResponse('_add', status='501 Not Implemented', content_type='text/plain')

    def test_bad_input(self):
        response, data = self.assertRPCResponse('add', [2, 4, 6])
        self.assertEquals(data.body.code, "TypeError")
        self.assertEquals(data.body.description, "add() takes exactly 3 arguments (4 given)")

    # TODO: Need to determine correct behaviour here.
    #       Currently will result in a 500 Internal Server Error in production.
    # def test_empty_request(self):
    #     request = Request.blank('/', method="POST", body="")
    #     response = request.get_response(self.app)
    #     self.assertEqual((response.status, response.content_type), ('411 Length Required', "text/plain"))

    def test_before(self):
        response, data = self.assertRPCResponse('add', [2, 4])
        self.assertEquals(self.root.args, (2, 4))

    def test_after(self):
        response, data = self.assertRPCResponse('add', [2, 4])
        self.assertEquals(self.root.result, 6)
