# encoding: utf-8

from unittest import TestCase
from nose.tools import raises
from web.core.middleware import defaultbool, MiddlewareWrapper, database, sessions

from common import PlainController


test_config = {
        'web.debug': False,
        'web.templating': False,
        'web.config': False,
        'web.widgets': False,
        'web.sessions': False,
        'web.compress': True,
        'web.profile': True,

        'web.static': True,
        'web.static.path': '/tmp'
    }


class RootController(PlainController):
    def index(self, *args, **kw):
        return "success"


class TestMiddlewareHelpers(TestCase):
    def test_defaultbool_literals(self):
        self.assertTrue(defaultbool(True))
        self.assertFalse(defaultbool(False))

    def test_defaultbool_true(self):
        self.assertTrue(defaultbool('true'))
        self.assertTrue(defaultbool('True'))
        self.assertTrue(defaultbool('on'))
        self.assertTrue(defaultbool('ON'))
        self.assertTrue(defaultbool('yes'))
        self.assertTrue(defaultbool('YES'))

    def test_defaultbool_false(self):
        self.assertFalse(defaultbool('false'))
        self.assertFalse(defaultbool('off'))
        self.assertFalse(defaultbool('no'))
        self.assertFalse(defaultbool('Bob Dole'))
        self.assertFalse(defaultbool(None))

    def test_defaultbool_extended(self):
        self.assertTrue(defaultbool('Bob Dole', ['bob dole']))

    def test_wrapper(self):
        class Inner(object):
            def __repr__(self):
                return "bar"

            def __call__(self):
                return 27

        w = MiddlewareWrapper(Inner(), 'foo', "bob")

        self.assertEqual(repr(w), "Wrapper(foo, 'bob') for bar")
        self.assertEqual(w(), 27)


class TestDatabaseMiddleware(TestCase):
    @raises(Exception)
    def test_bad_entrypoint(self):
        database(RootController, {
                'db.connections': 'foo',
                'db.foo.engine': 'bar'
            })

    @raises(ImportError)
    def test_bad_dotcolon(self):
        database(RootController, {
                'db.connections': 'foo',
                'db.foo.engine': 'web.extras.foo:Bar'
            })

    @raises(ImportError)
    def test_bad_model(self):
        database(RootController, {
                'db.connections': 'foo',
                'db.foo.model': 'web.extras.foo'
            })


class TestSessionsMiddleware(TestCase):
    def test_expire_true(self):
        sessions(RootController, {
                'web.sessions': True,
                'web.sessions.type': 'cookie',
                'web.sessions.cookie_expires': True
            })
        sessions(RootController, {
                'web.sessions': True,
                'web.sessions.type': 'cookie',
                'web.sessions.cookie_expires': 'True'
            })

    def test_expire_false(self):
        sessions(RootController, {
                'web.sessions': True,
                'web.sessions.type': 'cookie',
                'web.sessions.cookie_expires': False
            })
        sessions(RootController, {
                'web.sessions': True,
                'web.sessions.type': 'cookie',
                'web.sessions.cookie_expires': 'False'
            })

    def test_expire_time(self):
        sessions(RootController, {
                'web.sessions': True,
                'web.sessions.type': 'cookie',
                'web.sessions.cookie_expires': 60
            })
        sessions(RootController, {
                'web.sessions': True,
                'web.sessions.type': 'cookie',
                'web.sessions.cookie_expires': '120'
            })
