# coding: utf-8
from __future__ import unicode_literals, division, print_function, absolute_import

from copy import deepcopy

from nose.tools import eq_
from marrow.wsgi.objects.request import LocalRequest
from marrow.wsgi.objects.response import Response
from marrow import logging

from web.ext.authentication import AuthenticationExtension


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

    def save(self):
        self.persistent = deepcopy(self.current)


class DummyController(object):
    def dummymethod(self):
        pass

    def login(self, username, password):
        self._ctx.authenticate(username, password)


class TestAuthenticationExtension(object):
    dummy_user = {'username': 'foo', 'password': 'bar', 'fullname': 'Foo'}
    dummy_authenticate = lambda context, username, password: (1, TestAuthenticationExtension.dummy_user) \
            if username == 'foo' and password == 'bar' else (None, None)
    dummy_lookup = lambda context, uid: TestAuthenticationExtension.dummy_user if uid == 1 else None
    default_basic_config = {'method': 'basic', 'auth_callback': dummy_authenticate, 'lookup_callback': dummy_lookup}
    default_session_config = {'auth_callback': dummy_authenticate, 'lookup_callback': dummy_lookup}

    def _init_ext(self, config):
        self.ctx_class = type(b'Context', (object,), {'log': logging.log})
        self.ext = AuthenticationExtension(self.ctx_class, **config)
        self.ext.start(self.ctx_class)

    def test_basic_auth(self):
        self._init_ext(self.default_basic_config)
        context = self.ctx_class()
        context.request = LocalRequest({b'HTTP_AUTHORIZATION': b'basic Zm9vOmJhcg=='})
        context.response = Response(context.request)
        controller = DummyController()

        self.ext.prepare(context)
        self.ext.dispatch(context, '', controller, False)
        self.ext.dispatch(context, 'dummymethod', controller.dummymethod, True)

        eq_(context.user, self.dummy_user)

    def test_session_auth(self):
        self._init_ext(self.default_session_config)
        context = self.ctx_class()
        context.request = LocalRequest(POST={'username': 'foo', 'password': 'bar'})
        context.response = Response(context.request)
        controller = DummyController()

        self.ext.prepare(context)
        self.ext.dispatch(context, '', controller, False)
        self.ext.dispatch(context, 'login', controller.login, True)

        eq_(context.user, self.dummy_user)
        eq_(context.session.persistent['__user_id'], 1)
