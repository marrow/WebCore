# encoding: utf-8

from __future__ import unicode_literals

from webob import Request

from web.core import Application
from web.rpc.extdirect import ExtDirectController
from common import WebTestCase

try:
    from simplejson import dumps, loads
except ImportError:
    from json import dumps, loads


test_config = {'debug': False, 'web.widgets': False, 'web.compress': False, 'web.static': False}

class SubController(ExtDirectController):
    def multiply(self, a, b):
        return a * b


class RootController(ExtDirectController):
    def add(self, a, b):
        return int(a) + int(b)
        
    def error(self):
        raise Exception('Test Exception')
    
    sub = SubController()


class TestExtDirectRPC(WebTestCase):
    tid = 0
    app = Application.factory(root=RootController, **test_config)

    def assertRPCResponse(self, action, method, data=[], path='/', status='200 OK', content_type='application/json',
            **kw):
        self.tid += 1

        request = Request.blank(path, method="POST")
        request.body = dumps(dict(type='rpc', action=action, method=method, data=data, tid=self.tid))
        request.headers['Content-Type'] = 'application/json'

        response = request.get_response(self.app)

        self.assertEqual((response.status, response.content_type), (status, content_type))

        for i, j in kw.iteritems():
            self.assertEqual(getattr(response, i), j)

        data = None
        try:
            data = loads(response.body)
            self.assertEqual(data['tid'], self.tid)
        except:
            pass

        return response, data

    def testApi(self):
        response = self.assertResponse('/', content_type='application/json')
        api = loads(response.body)
        self.assertEqual(api, {
            'RootController': [
                {'name': 'add', 'len': 2},
                {'name': 'error', 'len': 0}
            ],
            'SubController': [
                {'name': 'multiply', 'len': 2}
            ]
        })

    def testCall(self):
        response, data = self.assertRPCResponse('RootController', 'add', [1, 3])
        self.assertEqual(data, {
            'type': 'rpc',
            'action': 'RootController',
            'method': 'add',
            'tid': 1,
            'result': 4
        })

    def testCallSubController(self):
        response, data = self.assertRPCResponse('SubController', 'multiply', [2, 3])
        self.assertEqual(data, {
            'type': 'rpc',
            'action': 'SubController',
            'method': 'multiply',
            'tid': 1,
            'result': 6
        })

    def testApplicationException(self):
        response, data = self.assertRPCResponse('RootController', 'error', status='500 Internal Server Error')
        module_path = __file__.replace('.pyc', '.py')
        self.assertEqual(data, {
            'type': 'exception',
            'action': 'RootController',
            'method': 'error',
            'tid': 1,
            'message': 'Test Exception',
            'where': '{0}:{1}'.format(module_path, 29)
        })

    def testMultiCall(self):
        request = Request.blank('/', method="POST")
        request.body = dumps([
            {'type': 'rpc', 'action': 'RootController', 'method': 'add', 'tid': 1, 'data': [1, 2]},
            {'type': 'rpc', 'action': 'SubController', 'method': 'multiply', 'tid': 2, 'data': [2, 4]}
        ])
        request.headers['Content-Type'] = 'application/json'
        response = request.get_response(self.app)
        self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))

        data = loads(response.body)
        results = [tx['result'] for tx in data]
        self.assertEqual(results, [3, 8])

    def testFormPost(self):
        data = {
            'extType': 'rpc',
            'extAction': 'RootController',
            'extMethod': 'add',
            'extUpload': 'false',
            'extTID': '1',
            'a': '2',
            'b': '5'
        }
        response = self.assertPostResponse('/', data=data, content_type='application/json')
        
        data = loads(response.body)
        self.assertEquals(data, {
            'type': 'rpc',
            'action': 'RootController',
            'method': 'add',
            'tid': '1',
            'result': 7
        })

    def testFormUpload(self):
        data = {
            'extType': 'rpc',
            'extAction': 'RootController',
            'extMethod': 'add',
            'extUpload': 'true',
            'extTID': '1',
            'a': '2',
            'b': '5'
        }
        response = self.assertPostResponse('/', data=data, content_type='text/html')
        
        self.assertEquals(response.ubody, '''\
<html><body><textarea>\
{\\"tid\\": \\"1\\", \\"action\\": \\"RootController\\", \\"type\\": \\"rpc\\", \\"method\\": \\"add\\", \\"result\\": 7}\
</textarea></body></html>''')
