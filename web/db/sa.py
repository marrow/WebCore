# encoding: utf-8

"""
"""


import re

import web

from paste.deploy.converters                    import asbool, asint
from paste.registry                             import StackedObjectProxy

from sqlalchemy                                 import engine_from_config
from sqlalchemy.orm                             import scoped_session, sessionmaker



__all__ = ['SQLAlchemyMiddleware']
log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')



class SQLAlchemyMiddleware(object):
    def __init__(self, application, prefix, model, session, **config):
        self.application, self.prefix, self.model, self.session, self.config = application, prefix, model, session, config.copy()
        
        log.info("Connecting SQLAlchemy to '%s'.", _safe_uri_replace.sub(r'\1://\2@', self.config.get('%s.sqlalchemy.url' % (self.prefix, ))))
        
        # Here we cheat a little to ensure the properties are assignable.
        for prop in ('engine', ):
            if not hasattr(self.model, prop):
                self.model.__dict__[prop] = None
        
        self.model.engine = engine_from_config(self.config, prefix="%s.sqlalchemy." % (self.prefix, ))
        self.model.metadata.bind = self.model.engine
        
        if config.get('%s.sqlalchemy.sqlsoup' % (self.prefix, ), False):
            from sqlalchemy.ext.sqlsoup import SqlSoup
            self.model.__dict__['soup'] = SqlSoup(self.model.metadata)
        
        if hasattr(self.model, 'populate') and callable(self.model.populate):
            for table in self.model.metadata.sorted_tables:
                table.append_ddl_listener('after-create', self.populate_table)
        
        if hasattr(self.model, 'prepare') and callable(self.model.prepare):
            self.model.prepare()
    
    def __call__(self, environ, start_response):
        log.debug("Preparing database session.")
        
        if self.config.get('%s.sqlsoup' % (self.prefix, ), False):
            from sqlalchemy.ext.sqlsoup import objectstore
            environ['paste.registry'].register(self.session, objectstore.current)
        
        else:
            environ['paste.registry'].register(self.session, scoped_session(sessionmaker(
                    bind = self.model.engine,
                    autoflush = asbool(self.config.get('%s.autoflush' % (self.prefix, ), True)),
                    twophase = asbool(self.config.get('%s.twophase' % (self.prefix, ), False))
                )))
        
        result = self.application(environ, start_response)
        
        status = web.core.response.status_int
        
        if status >= 400:
            log.warn("Rolling back database session due to unknown error.")
            self.session.rollback()
            return result

        log.debug("Committing database session.")
        # If we still have a session, commit.
        self.session.commit()
        
        # Optionally clear the cache.
        if not self.config.get('%s.cache' % (self.prefix, ), True):
            self.session.expunge_all()
        self.session.close()
        
        return result
    
    def populate_table(self, action, table, bind):
        session = scoped_session(sessionmaker(
                bind = bind,
                autoflush = asbool(self.config.get('%s.autoflush' % (self.prefix, ), True)),
                twophase = asbool(self.config.get('%s.twophase' % (self.prefix, ), False))
            ))
        
        try:
            self.model.populate(session, table.name)
        
        except: # pragma: no cover
            session.rollback()
            raise
        
        session.commit()
        
