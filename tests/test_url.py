# encoding: utf-8

import web

from nose.tools import eq_ as eq
from web.core import Application
from web.utils import URLGenerator
from common import PlainController, WebTestCase


class MockURLGenerator(URLGenerator):
    def __init__(self, base, full, controller):
        self.base = base
        self.full = full
        self.controller = controller

    @property
    def _base(self):
        return self.base, self.full, self.controller


def test_paths():
    url = MockURLGenerator('', 'http://example.com/foo/bar', '/foo')
    test_set = [
            ('', '/foo/bar'),
            ('/', '/'),
            ('/foo/bar', '/foo/bar'),
            ('baz', '/foo/baz')
        ]

    for i, o in test_set:
        yield eq, url(i), o


def test_urls():
    url = MockURLGenerator('', 'http://example.com/foo/bar', '/foo')
    test_set = [
            (dict(path='', protocol="https"), 'https://example.com/foo/bar'),
            (dict(path='/', host="google.com"), 'http://google.com/'),
            (dict(path='/foo/bar', port=8080), 'http://example.com:8080/foo/bar')
        ]

    for i, o in test_set:
        yield eq, url(**i), o


def test_arguments():
    url = MockURLGenerator('', 'http://example.com/foo/bar', '/foo')
    test_set = [
            (dict(path='', params=dict(text="Hello world.")), '/foo/bar?text=Hello+world.'),
            (dict(path='/', anchor="hello"), '/#hello')
        ]

    for i, o in test_set:
        yield eq, url(**i), o


def test_composition():
    url = MockURLGenerator('', 'http://example.com/foo/bar', '/foo')
    test_set = [
            ([], '/foo/bar'),
            (['/'], '/'),
            ([27, 'delete'], '/foo/27/delete')
        ]

    for i, o in test_set:
        yield eq, url.compose(*i), o


def test_nonroot_urls():
    url = MockURLGenerator('/app', 'http://example.com/app/foo/bar', '/app/foo')
    test_set = [
            (dict(path='', protocol="https"), 'https://example.com/app/foo/bar'),
            (dict(path='/', host="google.com"), 'http://google.com/app/'),
            (dict(path='/foo/bar', port=8080), 'http://example.com:8080/app/foo/bar')
        ]

    for i, o in test_set:
        yield eq, url(**i), o


def test_nonroot_arguments():
    url = MockURLGenerator('/app', 'http://example.com/app/foo/bar', '/app/foo')
    test_set = [
            (dict(path='', params=dict(text="Hello world.")), '/app/foo/bar?text=Hello+world.'),
            (dict(path='/', anchor="hello"), '/app/#hello')
        ]

    for i, o in test_set:
        yield eq, url(**i), o


def test_nonroot_composition():
    url = MockURLGenerator('/app', 'http://example.com/app/foo/bar', '/app/foo')
    test_set = [
            ([], '/app/foo/bar'),
            (['/'], '/app/'),
            ([27, 'delete'], '/app/foo/27/delete')
        ]

    for i, o in test_set:
        yield eq, url.compose(*i), o


class RootController(PlainController):
    def index(self):
        return "\n".join(web.core.url._base)


class TestURLContext(WebTestCase):
    app = Application.factory(root=RootController)

    def test_url_context(self):
        self.assertResponse('/', body="\nhttp://localhost/\n")
