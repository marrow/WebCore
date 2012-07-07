# encoding: utf-8

from unittest import TestCase
from nose.tools import raises
from web.core import Dialect
from web.rpc import route, RoutingError


class Foo(Dialect):
    def normal(self):
        return 1

    def _private(self):
        return 2

    bad = object()

    string = ""


Foo.deep = Foo()
Foo.deep2 = Dialect()


class TestRPCRouting(TestCase):
    def test_basic(self):
        self.assertEqual(route(Foo, 'normal', Dialect)[0], Foo.normal)

    @raises(RoutingError)
    def test_private(self):
        route(Foo, '_private', Dialect)

    @raises(RoutingError)
    def test_bad(self):
        route(Foo, 'bad', Dialect)

    @raises(RoutingError)
    def test_bad2(self):
        route(Foo, 'string', Dialect)

    @raises(RoutingError)
    def test_bad3(self):
        route(Foo, 'string.foo', Dialect)

    def test_deep(self):
        route(Foo, 'deep.normal', Dialect)

    @raises(RoutingError)
    def test_deep_failure(self):
        route(Foo, 'deep._private', Dialect)

    @raises(RoutingError)
    def test_context(self):
        route(Foo(), 'deep2.foo', Foo)

    @raises(RoutingError)
    def test_early_terminate(self):
        route(Foo, 'normal.foo', Dialect)
