# encoding: utf-8

"""
"""


import                                          re, web
from web.db.api                                 import IManager
from paste.deploy.converters                    import asbool, asint

from sqlalchemy                                 import engine_from_config
from sqlalchemy.orm                             import scoped_session, sessionmaker



__all__ = ['SQLAlchemyMiddleware']
log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


class SQLAlchemyMiddleware(IManager):
    def connect(self):
        log.info("Connecting to '%s'.", _safe_uri_replace.sub(r'\1://\2@', self.config.get('db.sqlalchemy.url')))
        
        if not hasattr(self.model, 'engine'):
            self.model.__dict__['engine'] = None
        
        self.model.engine = engine_from_config(self.config, prefix="db.sqlalchemy.")
        self.model.metadata.bind = self.model.engine
        
        #create_engine(
        #        web.config.db.connection,
        #        encoding = self.config.get('db.encoding', 'utf-8'),
        #        pool_size = asint(self.config.get('db.pool.size', 5)),
        #        pool_recycle = asint(self.config.get('db.pool.recycle', -1))
        #    )
    
    def __call__(self, environ, start_response):
        log.debug("Preparing database session.")
        
        environ.update({
                'orm': scoped_session(sessionmaker(
                        bind = self.model.engine,
                        autoflush = asbool(self.config.get('db.autoflush', True)),
                        twophase = asbool(self.config.get('db.twophase', False))
                    ))
            })
        
        try:
            return self.application(environ, start_response)
        
        except web.core.http.HTTPServerError:
            log.exception("Rolling back database session due to internal error.")
            environ['orm'].rollback()
            raise
        
        except web.core.http.HTTPException:
            log.exception("Committing database session for safe HTTP exception.")
            environ['orm'].commit()
            raise
        
        except:
            log.exception("Rolling back database session due to unknown error.")
            environ['orm'].rollback()
            raise
        
        finally:
            log.debug("Committing database session.")
            # If we still have a session, commit.
            environ['orm'].commit()
            
            # Optionally clear the cache.
            if not self.config.get('db.cache', True):
                environ['orm'].clear()
