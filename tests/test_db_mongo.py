# encoding: utf-8

from unittest import TestCase, skip

try:
    import pymongo
    from pymongo.errors import ConnectionFailure

except ImportError:
    skip("PyMongo not available; skipping tests which rely on it.")


try:
    connection = pymongo.Connection()
    
except ConnectionFailure:
    skip("Could not connect to local MongoDB server; skipping tests which rely on it.")

else:
    connection.disconnect()


def prepare():
    pass


def ready(db=None):
    pass


config = {'db.url': 'mongo://localhost/test', 'db.ready': ready}
connection = None
db = None


class TestMongo(TestCase):
    middleware = None
    
    @classmethod
    def setUpClass(cls):
        try:
            from web.db.mongo import MongoMiddleware
        
        except ImportError:
            skip("PyMongo not available; skipping MongoDB tests.")
        
        cls.middleware = MongoMiddleware
    
    def tearDown(self):
        global connection
        global db
        
        if connection:
            connection.disconnect()
            connection = None
        
        db = None
    
    def test_basic(self):
        self.middleware('db', __import__('test_db_mongo'), **config)
        
        self.assertEqual(connection.host, 'localhost')
        self.assertEqual(connection.port, 27017)
    
    def test_bad_scheme(self):
        lconfig = config.copy()
        lconfig['db.url'] = "foo://localhost/test"
        
        self.assertRaises(Exception, self.middleware, 'db', __import__('test_db_mongo'), **lconfig)


class TestMongoEngine(TestCase):
    middleware = None
    
    @classmethod
    def setUpClass(cls):
        try:
            from web.db.me import MongoEngineMiddleware
        
        except ImportError:
            skip("MongoEngine not available; skipping MongoEngine tests.")
        
        cls.middleware = MongoEngineMiddleware
    
    def test_basic(self):
        self.middleware('db', __import__('test_db_mongo'), **config)
    
    def test_bad_scheme(self):
        lconfig = config.copy()
        lconfig['db.url'] = "foo://localhost/test"
        
        self.assertRaises(Exception, self.middleware, 'db', __import__('test_db_mongo'), **lconfig)
