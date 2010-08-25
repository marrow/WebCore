# encoding: utf-8

import web.core
import web.auth
from web.core import Application
from web.auth.middleware import WebAuth
from web.utils.dictionary import adict

from paste.registry import StackedObjectProxy

from unittest import TestCase
from common import PlainController, WebTestCase



users = {'amcgregor': {'name': 'Alice Bevan-McGregor', 'pass': 'foo'}}

is_me = web.auth.CustomPredicate(lambda u, r: getattr(u, 'name', None) == "user")
user_in = web.auth.AttrIn.partial('name')
member_of = web.auth.ValueIn.partial('groups')
remote_addr_in = web.auth.EnvironIn.partial('REMOTE_ADDR')
local = remote_addr_in(['127.0.0.1', '::1', 'fe80::1%%lo0'])


def lookup(identifier):
    return users[identifier] if identifier in users else None

def authenticate(identifier, password):
    return (identifier, users[identifier]) if identifier in users and users[identifier]['pass'] == password else None


test_config = {
        'web.debug': False,
        'web.templating': False,
        'web.config': False,
        'web.widgets': False,
        'web.sessions': True,
        'web.sessions.type': 'cookie',
        'web.sessions.validate_key': 'foo',
        'web.cache': False,
        'web.compress': False,
        'web.profile': False,
        'web.static': False,
        'web.auth': True,
        'web.auth.lookup': lookup,
        'web.auth.authenticate': authenticate
    }


class RootController(PlainController):
    def index(self, *args, **kw):
        return "success"
    
    @web.auth.authorize(web.auth.anonymous)
    def anonymous(self):
        return "anonymous"
    
    @web.auth.authorize(web.auth.authenticated)
    def authenticated(self):
        return "authenticated"
    
    @web.auth.authorize(local)
    def local(self):
        return "local"
    
    def authenticate(self, username, password):
        return "ok" if web.auth.authenticate(username, password) else "error"
    
    def force(self, username):
        return "ok" if web.auth.authenticate(username, None, force=True) else "error"
    
    def kill(self):
        web.auth.deauthenticate()
        return "ok"
    
    def nuke(self):
        web.auth.deauthenticate(True)
        return "ok"


class TestWebAuthMiddleware(WebTestCase):
    def test_exceptions(self):
        self.assertRaises(Exception, lambda: WebAuth(None))


class TestAuthApp(WebTestCase):
    app = Application.factory(root=RootController, **test_config)
    
    def test_index(self):
        self.assertResponse('/', body="success")
    
    def test_anonymous(self):
        self.assertResponse('/anonymous', body="anonymous")
        self.assertResponse('/authenticated', '307 Temporary Redirect', 'text/html')
    
    def check_authentication(self, url, expected_body):
        print url, expected_body
        assert False
        # self.assertResponse(url, body=expected_body)
    
    def test_authentication_not_existant(self):
        pairs = [
                ('/authenticate?username=nobody&password=baz', "error"),
                ('/authenticate?username=amcgregor&password=bar', "error"),
                ('/authenticate?username=amcgregor&password=foo', "ok"),
                ('/force?username=nobody', "error"),
                ('/force?username=amcgregor', "ok"),
                ('/kill', "ok")
            ]
        
        for url, expected_body in pairs:
            yield self.check_authentication, url, expected_body
    
    # def test_authentication(self):
    #     # TODO: Functional testing; ensure the session and thread-local are set.
    #     self.assertResponse('/authenticate?username=nobody&password=baz', body="error")
    #     self.assertResponse('/authenticate?username=amcgregor&password=bar', body="error")
    #     self.assertResponse('/authenticate?username=amcgregor&password=foo', body="ok")
    #     self.assertResponse('/force?username=nobody', body="error")
    #     self.assertResponse('/force?username=amcgregor', body="ok")
    #     self.assertResponse('/kill', body="ok")
    
    def test_deauthenticate(self):
        # TODO: Functional testing; ensure the session and thread-local are cleared.
        self.assertResponse('/kill', body="ok")
        self.assertResponse('/nuke', body="ok")
    
    def test_local(self):
        self.assertResponse('/local', body="local")


class TestAnonymousPredicates(TestCase):
    def setUp(self):
        web.auth.user = None
    
    def tearDown(self):
        web.auth.user = StackedObjectProxy(name="user")
    
    def test_basics(self):
        self.assertRaises(NotImplementedError, lambda: bool(web.auth.Predicate()))
        
        self.failIf(web.auth.never)
        self.failUnless(web.auth.always)
        self.failUnless(web.auth.Not(web.auth.never))
    
    def test_combinations(self):
        self.failUnless(web.auth.All(web.auth.always, web.auth.always))
        self.failIf(web.auth.All(web.auth.always, web.auth.never))
        self.failUnless(web.auth.Any(web.auth.always, web.auth.never))
    
    def test_anonymous(self):
        self.failUnless(web.auth.anonymous)
        self.failIf(web.auth.authenticated)
    
    def test_authenticated(self):
        self.failIf(is_me)
        self.failIf(user_in(['jrh', 'user']))
        self.failIf(member_of('admin'))


class sadict(adict):
    def _current_obj(self):
        return self


class TestAuthenticatedPredicates(TestCase):
    def setUp(self):
        web.auth.user = sadict(name="user", groups=["admin"])

    def tearDown(self):
        web.auth.user = StackedObjectProxy(name="user")

    def test_anonymous(self):
        self.failIf(web.auth.anonymous)
        self.failUnless(web.auth.authenticated)
    
    def test_authenticated(self):
        self.failUnless(is_me)
        self.failUnless(user_in(['jrh', 'user']))
        self.failUnless(member_of('admin'))
