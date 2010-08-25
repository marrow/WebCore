# encoding: utf-8

"""
"""


import re

from pymongo.connection import Connection



__all__ = ['MongoMiddleware']
log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')



def MongoMiddleware(application, prefix, model, session=None, **config):
    url = config.get('%s.url' % (prefix, ), 'mongo://localhost')
    
    log.info("Connecting Mongo to '%s'.", _safe_uri_replace.sub(r'\1://\2@', url))
    
    scheme, parts = url.split('://', 1)
    parts, db = parts.split('/', 1)
    auth, host = parts.split('@', 1) if '@' in parts else (None, parts)
    
    if scheme != 'mongo':
        raise Exception('The URL must begin with \'mongo://\'!')
    
    host, port = host.split(':') if ':' in host else (host, '27017')
    
    log.debug("Connection: %r", (scheme, auth.split(':', 1) if auth else [None, None], host, port, db))
    
    model.__dict__['connection'] = Connection(host if host else 'localhost', int(port))
    model.__dict__['db'] = model.connection[db]
    
    if auth and not model.db.authenticate(*auth.split(':', 1)):
        raise Exception("Error attempting to authenticate to MongoDB.")
    
    prepare = getattr(model, 'prepare', None)
    if hasattr(prepare, '__call__'):
        prepare()
    
    return application
