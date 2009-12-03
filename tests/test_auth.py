# encoding: utf-8

import web, web.auth
from web.core import Application
from web.utils.dictionary import adict

from paste.registry import StackedObjectProxy

from unittest import TestCase
from common import PlainController, WebTestCase


def lookup(identifier):
    return None

def authenticate(identifier, password, force=False):
    return None


is_me = web.auth.CustomPredicate(lambda u, r: getattr(u, 'name', None) == "user")
user_in = web.auth.AttrIn.partial('name')
member_of = web.auth.ValueIn.partial('groups')
remote_addr_in = EnvironIn.partial('REMOTE_ADDR')
local = remote_addr_in(['127.0.0.1', '::1', 'fe80::1%%lo0'])


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


class TestAuthApp(WebTestCase):
    app = Application.factory(root=RootController, **test_config)
    
    def test_index(self):
        self.assertResponse('/', body="success")
    
    def test_anonymous(self):
        self.assertResponse('/anonymous', body="anonymous")
        self.assertResponse('/authenticated', '307 Temporary Redirect', 'text/html')
    
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
