# encoding: utf-8

"""
"""


import re

import web

from paste.deploy.converters import asbool, asint
from paste.registry import StackedObjectProxy

from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker



__all__ = ['SQLAlchemyMiddleware']
log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')



class SQLAlchemyMiddleware(object):
    def __init__(self, application, prefix, model, session, **config):
        self.application, self.prefix, self.model, self.session, self.config = application, prefix, model, session, config.copy()
        
        log.info("Connecting SQLAlchemy to '%s'.", _safe_uri_replace.sub(r'\1://\2@', self.config.get('%s.sqlalchemy.url' % (self.prefix, ))))
        
        # Here we cheat a little to ensure the properties are assignable.
        for prop in ('engine'):
            if not hasattr(self.model, prop):
                self.model.__dict__[prop] = None
        
        self.model.engine = engine_from_config(self.config, prefix="%s.sqlalchemy." % (self.prefix, ))
        self.model.metadata.bind = self.model.engine
        
        if config.get('%s.sqlalchemy.sqlsoup' % (self.prefix, ), False):
            from sqlalchemy.ext.sqlsoup import SqlSoup, Session
            self.model.__dict__['soup'] = SqlSoup(self.model.metadata)
            self._session = Session
        
        else:
            self._session = sessionmaker(
                    bind = self.model.engine,
                    autocommit = asbool(self.config.get('%s.autocommit' % (self.prefix, ), False)),
                    autoflush = asbool(self.config.get('%s.autoflush' % (self.prefix, ), True)),
                    twophase = asbool(self.config.get('%s.twophase' % (self.prefix, ), False))
                )
        
        if hasattr(self.model, 'populate') and callable(self.model.populate):
            for table in self.model.metadata.sorted_tables:
                table.append_ddl_listener('after-create', self.populate_table)
        
        if hasattr(self.model, 'prepare') and callable(self.model.prepare):
            self.model.prepare()
    
    def __call__(self, environ, start_response):
        log.debug("Preparing database session.")
        
        if self.config.get('%s.sqlsoup' % (self.prefix, ), False):
            environ['paste.registry'].register(self.session, self._session.current)
        
        else:
            environ['paste.registry'].register(self.session, self._session())
        
        status = []
        
        def local_start(stat_str, headers=[]):
            status.append(int(stat_str.split(' ')[0]))
            return start_response(stat_str, headers)
        
        result = self.application(environ, local_start)
        
        if self.session.transaction is not None:
            if len(status) != 1 or status[0] >= 400:
                if status[0] >= 500:
                    log.warn("Rolling back database session due to HTTP status: %r", status[0])
                else:
                    log.debug("Rolling back database session due to HTTP status: %r", status[0])
            
                self.session.rollback()
            
            else:
                log.debug("Committing database session; HTTP status: %r", status[0])
                self.session.commit()
        
        self.session.close()
        
        return result
    
    def populate_table(self, action, table, bind):
        session = self._session()
        
        try:
            self.model.populate(session, table.name)
        
        except: # pragma: no cover
            session.rollback()
            raise
        
        session.commit()
        
