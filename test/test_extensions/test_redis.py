# coding: utf-8
from __future__ import unicode_literals, division, print_function, absolute_import

from nose.tools import eq_
from nose.plugins.skip import SkipTest
from marrow.wsgi.objects.request import LocalRequest
from redis.exceptions import ConnectionError
from redis import StrictRedis

from web.core.application import Application


def insert_data_controller(context):
    context.redis.set('bar', 'baz')


class TestRedisExtension(object):
    def setup(self):
        self.connection = StrictRedis(db='testdb')
        try:
            self.connection.ping()
        except ConnectionError:
            raise SkipTest('No Redis server available')

        self.config = {
                'extensions': {
                        'redis': {
                                'connection': self.connection
                            }
                    }
            }

    def teardown(self):
        self.connection.flushdb()

    def test_data_insert(self):
        app = Application(insert_data_controller, self.config)
        request = LocalRequest()
        status, headers, body = app(request.environ)

        eq_(status, b'200 OK')
        eq_(self.connection['bar'], 'baz')
