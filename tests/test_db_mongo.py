# encoding: utf-8
import pymongo
from pymongo.errors import AutoReconnect
from nose import SkipTest
from nose.tools import eq_, assert_raises

from web.db.mongo import MongoMiddleware
from web.db.me import MongoEngineMiddleware


try:
    connection = pymongo.Connection('localhost', 27017)
except AutoReconnect:
    connection = None
else:
    connection.disconnect()


def prepare():
    pass


def ready(db=None):
    pass


config = {'db.url': 'mongo://localhost/test', 'db.ready': ready}
db = None


class TestMongo(object):
    def setUp(self):
        if connection is None:
            raise SkipTest("Could not connect to local MongoDB server; skipping tests which rely on it.")

    def tearDown(self):
        global connection
        global db

        if connection:
            connection.disconnect()

        db = None

    def test_basic(self):
        MongoMiddleware(self, 'db', __import__('test_db_mongo'), **config)

        eq_(connection.host, 'localhost')
        eq_(connection.port, 27017)

    def test_bad_scheme(self):
        lconfig = config.copy()
        lconfig['db.url'] = "foo://localhost/test"

        assert_raises(Exception, MongoMiddleware, self, 'db', __import__('test_db_mongo'), **lconfig)


class TestMongoEngine(object):
    def setUp(self):
        if connection is None:
            raise SkipTest("Could not connect to local MongoDB server; skipping tests which rely on it.")

    def test_basic(self):
        MongoEngineMiddleware(self, 'db', __import__('test_db_mongo'), **config)

    def test_bad_scheme(self):
        lconfig = config.copy()
        lconfig['db.url'] = "foo://localhost/test"

        assert_raises(Exception, MongoEngineMiddleware, self, 'db', __import__('test_db_mongo'), **lconfig)
