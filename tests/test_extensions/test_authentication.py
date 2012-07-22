# coding: utf-8
from __future__ import unicode_literals, division, print_function, absolute_import

from nose.tools import eq_
from marrow.wsgi.objects.request import LocalRequest
from marrow.wsgi.objects.response import Response
from marrow import logging

from web.ext.authentication import AuthenticationExtension


class DummyController(object):
    def dummymethod(self):
        pass


class TestAuthenticationExtension(object):
    dummy_user = {'username': 'foo', 'password': 'bar', 'fullname': 'Foo'}
    dummy_authenticate = lambda context, username, password: (1, TestAuthenticationExtension.dummy_user) \
            if username == 'foo' and password == 'bar' else (None, None)
    dummy_lookup = lambda context, uid: TestAuthenticationExtension.dummy_user if uid == 1 else None
    default_basic_config = {'method': 'basic', 'realm': 'test realm', 'auth_callback': dummy_authenticate,
            'lookup_callback': dummy_lookup}
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
