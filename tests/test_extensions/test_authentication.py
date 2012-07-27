# coding: utf-8

from __future__ import unicode_literals, division, print_function, absolute_import

from json import dumps, loads
from copy import deepcopy

from nose.tools import eq_
from marrow.wsgi.objects.request import LocalRequest
from marrow.wsgi.objects.response import Response
from marrow import logging

from web.ext.authentication import AuthenticationExtension
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


class DummyController(object):
    def __init__(self, context):
        self._ctx = context
    
    def dummymethod(self):
        pass


def login(context, username, password):
    context.authenticate(username, password)
    context.response.charset = 'utf8'
    return dumps([context.user, context.session.persistent])


class TestAuthenticationExtension(object):
    dummy_user = {'username': 'foo', 'password': 'bar', 'fullname': 'Foo'}
    dummy_authenticate = lambda context, username, password: (1, TestAuthenticationExtension.dummy_user) \
            if username == 'foo' and password == 'bar' else (None, None)
    dummy_lookup = lambda context, uid: TestAuthenticationExtension.dummy_user if uid == 1 else None
    default_basic_config = {'method': 'basic', 'auth_callback': dummy_authenticate, 'lookup_callback': dummy_lookup}
    default_session_config = {
            'extensions': {
                    'authentication': {
                            'auth_callback': dummy_authenticate,
                            'lookup_callback': dummy_lookup
                            }
                    }
    }

    class Context(object):
        log = logging.log
    
    def _init_ext(self, config):
        self.ext = AuthenticationExtension(self.Context, **config)
        self.ext.start(self.Context)

    def test_basic_auth(self):
        self._init_ext(self.default_basic_config)
        context = self.Context()
        context.request = LocalRequest({b'HTTP_AUTHORIZATION': b'basic Zm9vOmJhcg=='})
        context.response = Response(context.request)
        controller = DummyController(context)
    
        self.ext.prepare(context)
        self.ext.dispatch(context, '', controller, False)
        self.ext.dispatch(context, 'dummymethod', controller.dummymethod, True)
    
        eq_(context.user, self.dummy_user)

    def test_session_auth(self):
        app = Application(login, self.default_session_config)
        app.Context.session = MockSession()
        request = LocalRequest(path='/?username=foo&password=bar')
        status, headers, body = app(request.environ)

        user, session = loads(b''.join(body).decode('utf8'))

        eq_(status, b'200 OK')
        eq_(user, self.dummy_user)
        eq_(session['__user_id'], 1)
