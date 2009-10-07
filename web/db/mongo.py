# encoding: utf-8

"""
"""


import re

from urlparse import urlparse

import web

from pymongo.connection import Connection



__all__ = ['MongoMiddleware']
log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')



class MongoMiddleware(object):
    def __init__(self, application, prefix, model, session=None, **config):
        self.application, self.prefix, self.model, self.config = application, prefix, model, config.copy()
        
        url = self.config.get('%s.url' % (self.prefix, ), 'mongo://localhost')
        
        log.info("Connecting Mongo to '%s'.", _safe_uri_replace.sub(r'\1://\2@', url))
        
        scheme, parts = url.split('://', 1)
        parts, db = parts.split('/', 1)
        auth, host = parts.split('@', 1) if '@' in parts else (None, parts)
        
        if scheme != 'mongo':
            raise Exception('The URL must begin with \'mongo://\'!')
        
        host, port = host.split(':') if ':' in host else (host, '27017')
        
        self.model.__dict__['connection'] = Connection(host if host else 'localhost', int(port))
        self.model.__dict__['db'] = self.model.connection[db]
        
        if auth and not self.model.db.authenticate(*auth.split(':', 1)):
            raise Exception("Error attempting to authenticate to MongoDB.")
        
        if hasattr(self.model, 'prepare') and callable(self.model.prepare):
            self.model.prepare()
    
    def __call__(self, environ, start_response):
        return self.application(environ, start_response)
