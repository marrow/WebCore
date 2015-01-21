# coding: utf-8
from __future__ import unicode_literals, division, print_function, absolute_import

from nose.tools import eq_
from nose.plugins.skip import SkipTest
from marrow.wsgi.objects.request import LocalRequest
from pymongo import Connection
from pymongo.errors import AutoReconnect

from web.core.application import Application


def insert_data_controller(context):
    collection = context.mongodb['testdb']['testcollection']
    collection.insert({'bar': 'baz'})


class TestMongoDBExtension(object):
    def setup(self):
        try:
            self.connection = Connection()
        except AutoReconnect:
            raise SkipTest('No MongoDB server available')

        self.config = {
                'extensions': {
                        'mongodb': {
                                'connection': self.connection
                            }
                    }
            }

    def teardown(self):
        self.connection.drop_database('testdb')

    def test_data_insert(self):
        app = Application(insert_data_controller, self.config)
        request = LocalRequest()
        status, headers, body = app(request.environ)

        obj = self.connection['testdb']['testcollection'].find_one()
        eq_(status, b'200 OK')
        eq_(obj['bar'], 'baz')
