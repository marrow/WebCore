# encoding: utf-8

"""
"""


import                                          re, web
from paste.deploy.converters                    import asbool, asint
from paste.registry                             import StackedObjectProxy

from sqlalchemy                                 import engine_from_config
from sqlalchemy.orm                             import scoped_session, sessionmaker


__all__ = ['SQLAlchemyMiddleware']
log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')



class SQLAlchemyMiddleware(object):
    def __init__(self, application, model, **config):
        self.application, self.model, self.config = application, model, config.copy()
        
        log.info("Connecting SQLAlchemy to '%s'.", _safe_uri_replace.sub(r'\1://\2@', self.config.get('db.sqlalchemy.url')))
        
        # Here we cheat a little to ensure the properties are assignable.
        for prop in ('engine', 'session'):
            if not hasattr(self.model, prop):
                self.model.__dict__[prop] = None
        
        self.model.engine = engine_from_config(self.config, prefix="db.sqlalchemy.")
        self.model.metadata.bind = self.model.engine
        self.model.session = StackedObjectProxy()
    
    def __call__(self, environ, start_response):
        log.debug("Preparing database session.")
        
        environ['paste.registry'].register(self.model.session, scoped_session(sessionmaker(
                bind = self.model.engine,
                autoflush = asbool(self.config.get('db.autoflush', True)),
                twophase = asbool(self.config.get('db.twophase', False))
            )))
        
        try:
            return self.application(environ, start_response)
        
        except web.core.http.HTTPError:
            log.exception("Rolling back database session due to internal error.")
            self.model.session.rollback()
            raise
        
        except web.core.http.HTTPOk, web.core.http.HTTPRedirection:
            log.exception("Committing database session for safe HTTP exception.")
            self.model.session.commit()
            raise
        
        except:
            log.exception("Rolling back database session due to unknown error.")
            self.model.session.rollback()
            raise
        
        finally:
            log.debug("Committing database session.")
            # If we still have a session, commit.
            self.model.session.commit()
            
            # Optionally clear the cache.
            if not self.config.get('db.cache', True):
                self.model.session.expunge_all()
