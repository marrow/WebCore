# coding: utf-8

from __future__ import unicode_literals, division, print_function, absolute_import

from json import dumps, loads
from copy import deepcopy

from nose.tools import eq_
from marrow.wsgi.objects.request import LocalRequest

from web.core.application import Application


class MockSession(object):
    def __init__(self):
        self.persistent = {}
        self.current = {}

    def __getitem__(self, key):
        return self.current[key]

    def __setitem__(self, key, value):
        self.current[key] = value

    def __contains__(self, key):
        return key in self.current

    def get(self, key):
        return self.current.get(key)

    def save(self):
        self.persistent = deepcopy(self.current)


def basic_auth_method(context):
    return dumps(context.user)


def login(context, username, password):
    context.authenticate(username, password)
    context.response.charset = 'utf8'
    return dumps([context.user, context.session.persistent])


class TestAuthenticationExtension(object):
    dummy_user = {'username': 'foo', 'password': 'bar', 'fullname': 'Foo'}
    dummy_authenticate = lambda context, username, password: (1, TestAuthenticationExtension.dummy_user) \
            if username == 'foo' and password == 'bar' else (None, None)
    dummy_lookup = lambda context, uid: TestAuthenticationExtension.dummy_user if uid == 1 else None
    default_basic_config = {
            'extensions': {
                    'authentication': {
                            'method': 'basic',
                            'auth_callback': dummy_authenticate,
                            }
                    }
            }
    default_session_config = {
            'extensions': {
                    'authentication': {
                            'auth_callback': dummy_authenticate,
                            'lookup_callback': dummy_lookup
                            }
                    }
            }

    def test_basic_auth(self):
        app = Application(basic_auth_method, self.default_basic_config)
        request = LocalRequest({b'HTTP_AUTHORIZATION': b'basic Zm9vOmJhcg=='})
        status, headers, body = app(request.environ)

        user = loads(b''.join(body).decode('utf-8'))

        eq_(status, b'200 OK')
        eq_(user, self.dummy_user)

    def test_session_auth(self):
        app = Application(login, self.default_session_config)
        app.Context.session = MockSession()
        request = LocalRequest(POST={'username': 'foo', 'password': 'bar'})
        status, headers, body = app(request.environ)

        user, session = loads(b''.join(body).decode('utf-8'))

        eq_(status, b'200 OK')
        eq_(user, self.dummy_user)
        eq_(session['__user_id'], 1)
