# encoding: utf-8

from webob import Request
from web.core import Application
from web.rpc.jsonrpc import JSONRPCController
from common import WebTestCase

try:
    from simplejson import dumps, loads
except ImportError:
    from json import dumps, loads


test_config = {'debug': False, 'web.widgets': False, 'web.compress': False, 'web.static': False}


class RootController(JSONRPCController):
    def test(self):
        return "ok"

    def add(self, a, b):
        return a + b


class BadController(JSONRPCController):
    def test(self):
        return "ok"

    def __after__(self, result):
        return self.nonexisting


class TestJSONRPC(WebTestCase):
    id_ = 0
    app = Application.factory(root=RootController, **test_config)

    def assertRPCResponse(self, method, params=[], path='/', status='200 OK', content_type='application/json', **kw):
        self.id_ += 1

        request = Request.blank(path, method="POST")
        request.body = dumps(dict(method=method, params=params, id=self.id_))

        response = request.get_response(self.app)

        self.assertEqual((response.status, response.content_type), (status, content_type))

        for i, j in kw.iteritems():
            self.assertEqual(getattr(response, i), j)

        data = None
        try:
            data = loads(response.body)
            self.assertEqual(data['id'], self.id_)
        except:
            pass

        return response, data

    def test_basic(self):
        response, data = self.assertRPCResponse('test')
        self.assertEquals(data['result'], 'ok')

    def test_bad_method(self):
        response, data = self.assertRPCResponse('add', status='500 Internal Server Error', content_type='application/json')
        self.assertEquals(data, dict(
                id=1,
                result=None,
                error=dict(
                        message='add() takes exactly 3 arguments (1 given)',
                        code=100,
                        name='JSONRPCError',
                        error='Not disclosed.'
                    )
            ))

    def test_good_method(self):
        response, data = self.assertRPCResponse('add', [27, 42])
        self.assertEquals(data['result'], 69)

    def test_non_post(self):
        self.assertResponse('/', status='405 Method Not Allowed', content_type='text/plain')

    def test_private(self):
        self.assertRPCResponse('_add', status='501 Not Implemented', content_type='text/plain')

    def test_bad_input(self):
        self.assertRPCResponse('add', dict(foo="bar"), status='400 Bad Request', content_type='text/plain')

    def test_bad_json_input(self):
        request = Request.blank('/', method="POST", body="[foo")
        response = request.get_response(self.app)
        self.assertEqual((response.status, response.content_type), ('400 Bad Request', 'text/plain'))

    def test_missing_method(self):
        request = Request.blank('/', method="POST", body='{"params": [], "id": null}')
        response = request.get_response(self.app)
        self.assertEqual((response.status, response.content_type), ('400 Bad Request', 'text/plain'))
        assert response.body.rstrip().endswith('Missing required JSON-RPC value: method')

    def test_missing_params(self):
        request = Request.blank('/', method="POST", body='{"method": "test", "id": null}')
        response = request.get_response(self.app)
        self.assertEqual((response.status, response.content_type), ('400 Bad Request', 'text/plain'))
        assert response.body.rstrip().endswith('Missing required JSON-RPC value: params')

    def test_missing_id(self):
        request = Request.blank('/', method="POST", body='{"method": "test", "params": []}')
        response = request.get_response(self.app)
        self.assertEqual((response.status, response.content_type), ('400 Bad Request', 'text/plain'))
        assert response.body.rstrip().endswith('Missing required JSON-RPC value: id')

    def test_after_attribute_exception(self):
        self.app = Application.factory(root=BadController, **test_config)
        response, data = self.assertRPCResponse('test', status='500 Internal Server Error', content_type='application/json')
        self.assertEquals(data, dict(
                id=1,
                result=None,
                error=dict(
                        message="'BadController' object has no attribute 'nonexisting'",
                        code=100,
                        name='JSONRPCError',
                        error='Not disclosed.'
                    )
            ))
