# encoding: utf-8

"""SQLAlchemy and SQLSoup transactional database integration."""


import api
import warnings

from paste.deploy.converters import asbool, aslist

from web.utils.object import get_dotted_object

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker



__all__ = ['SQLAlchemyMiddleware']
log = __import__('logging').getLogger(__name__)




class SQLAlchemyMiddleware(api.TransactionalMiddlewareInterface):
    def __init__(self, application, prefix, model, session, **config):
        self.config = {'%s.sqlalchemy.pool_recycle' % prefix: 3600}
        
        if ('%s.sqlalchemy.url' % prefix) in config:
            # Some compatability cruft; will be removed in 1.0.
            warnings.warn('%s.sqlalchemy.url is deprecated, use %s.url instead.' % (prefix, prefix), category=DeprecationWarning)
            config['%s.url' % prefix] = config['%s.sqlalchemy.url' % prefix]
        
        else:
            config['%s.sqlalchemy.url' % prefix] = config['%s.url' % prefix]
        
        self.soup = config.get('%s.sqlsoup' % prefix, False)
        
        super(SQLAlchemyMiddleware, self).__init__(application, prefix, model, session, **config)
    
    def setup(self):
        self.model.__dict__['engine'] = engine_from_config(self.config, prefix="%s.sqlalchemy." % (self.prefix, ))
        self.model.metadata.bind = self.model.engine
        
        if self.soup:
            from sqlalchemy.ext.sqlsoup import SqlSoup, Session
            self.model.__dict__['soup'] = SqlSoup(self.model.metadata)
            self._session = Session
        
        else:
            args = dict(
                    bind = self.model.engine,
                    autocommit = asbool(self.config.get('%s.autocommit' % (self.prefix, ), False)),
                    autoflush = asbool(self.config.get('%s.autoflush' % (self.prefix, ), True)),
                    twophase = asbool(self.config.get('%s.twophase' % (self.prefix, ), False)),
                )
            
            extensions_key = '%s.extensions' % (self.prefix, )
            if extensions_key in self.config:
                args['extensions'] = [get_dotted_object(i)() for i in aslist(self.config[extensions_key])]
            
            setup = getattr(self.model, 'setup', None)
            if hasattr(setup, '__call__'):
                args = setup(args)
            
            self._session = sessionmaker(**args)
        
        populate = getattr(self.model, 'populate', None)
        if hasattr(populate, '__call__'):
            for table in self.model.metadata.sorted_tables:
                table.append_ddl_listener('after-create', self.populate_table)
    
    def begin(self, environ):
        if self.soup:
            environ['paste.registry'].register(self.session, self._session.current)
        
        else:
            environ['paste.registry'].register(self.session, self._session())
    
    def vote(self, environ, status):
        if status >= 400:
            log.debug("Rolling back database session due to HTTP status: %r", status)
            return False
        
        log.debug("Committing database session; HTTP status: %r", status)
        return True
    
    def finish(self, environ):
        if self.session.transaction is not None: # use getattr
            self.session.commit()
            self.session.close()
    
    def abort(self, environ):
        if self.session.transaction is not None: # use getattr
            self.session.rollback()
            self.session.close()
    
    def populate_table(self, action, table, bind):
        session = self._session()
        
        try:
            self.model.populate(session, table.name)
        
        except: # pragma: no cover
            session.rollback()
            raise
        
        session.commit()
        
