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
    def __init__(self, application, prefix, model, session, **config):
        self.application, self.prefix, self.model, self.session, self.config = application, prefix, model, session, config.copy()
        
        log.info("Connecting SQLAlchemy to '%s'.", _safe_uri_replace.sub(r'\1://\2@', self.config.get('%s.sqlalchemy.url' % (self.prefix, ))))
        
        # Here we cheat a little to ensure the properties are assignable.
        for prop in ('engine', ):
            if not hasattr(self.model, prop):
                self.model.__dict__[prop] = None
        
        self.model.engine = engine_from_config(self.config, prefix="%s.sqlalchemy." % (self.prefix, ))
        self.model.metadata.bind = self.model.engine
        
        if hasattr(self.model, 'prepare') and callable(self.model.prepare):
            self.model.prepare()
    
    def __call__(self, environ, start_response):
        log.debug("Preparing database session.")
        
        environ['paste.registry'].register(self.session, scoped_session(sessionmaker(
                bind = self.model.engine,
                autoflush = asbool(self.config.get('%s.autoflush' % (self.prefix, ), True)),
                twophase = asbool(self.config.get('%s.twophase' % (self.prefix, ), False))
            )))
        
        try:
            return self.application(environ, start_response)
        
        except web.core.http.HTTPError:
            log.exception("Rolling back database session due to internal error.")
            self.session.rollback()
            raise
        
        except web.core.http.HTTPOk, web.core.http.HTTPRedirection:
            log.exception("Committing database session for safe HTTP exception.")
            self.session.commit()
            raise
        
        except:
            log.exception("Rolling back database session due to unknown error.")
            self.session.rollback()
            raise
        
        finally:
            log.debug("Committing database session.")
            # If we still have a session, commit.
            self.session.commit()
            
            # Optionally clear the cache.
            if not self.config.get('%s.cache' % (self.prefix, ), True):
                self.session.expunge_all()
            self.session.close()
