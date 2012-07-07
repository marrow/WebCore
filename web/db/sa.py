# encoding: utf-8

"""SQLAlchemy transactional database integration."""


import warnings
import api

from sqlalchemy import engine_from_config, event
from sqlalchemy.orm import sessionmaker
from marrow.util.convert import boolean
from marrow.util.object import load_object


__all__ = ['SQLAlchemyMiddleware']
log = __import__('logging').getLogger(__name__)


class SQLAlchemyMiddleware(api.TransactionalMiddlewareInterface):
    def __init__(self, application, prefix, model, session, **config):
        cfg = {
                '%s.sqlalchemy.pool_recycle' % prefix: 3600,
                '%s.sqlalchemy.url' % prefix: config['%s.url' % prefix]
            }
        cfg.update(config)

        super(SQLAlchemyMiddleware, self).__init__(application, prefix, model, session, **cfg)

    def setup(self):
        self.model.__dict__['engine'] = engine_from_config(self.config, prefix="%s.sqlalchemy." % (self.prefix,))

        self.model.metadata.bind = self.model.engine
        args = dict(
                bind=self.model.engine,
                autocommit=boolean(self.config.get('%s.autocommit' % (self.prefix,), False)),
                autoflush=boolean(self.config.get('%s.autoflush' % (self.prefix,), True)),
                twophase=boolean(self.config.get('%s.twophase' % (self.prefix,), False)),
            )

        setup = getattr(self.model, 'setup', None)
        if hasattr(setup, '__call__'):
            warnings.warn("Use of the hard-coded 'setup' callback is deprecated.\n"
                    "Use the 'ready' callback instead.", DeprecationWarning)
            args = setup(args)

        self._session = sessionmaker(**args)

    def ready(self):
        super(SQLAlchemyMiddleware, self).ready()

        populate = getattr(self.model, 'populate', None)
        if hasattr(populate, '__call__'):
            warnings.warn("Use of the hard-coded 'populate' callback is deprecated.\n"
                    "Use the 'ready' callback instead.", DeprecationWarning)

            for table in self.model.metadata.sorted_tables:
                event.listen(table, 'after_create', self.populate_table)

        cb = self.config.get(self.prefix + '.ready', None)

        if cb is not None:
            cb = load_object(cb) if isinstance(cb, basestring) else cb

            if hasattr(cb, '__call__'):
                cb(self._session)

    def begin(self, environ):
        environ['paste.registry'].register(self.session, self._session())

    def vote(self, environ, status, exc=None):
        if exc:
            log.debug("Rolling back database session due to internal error: %r", exc)
            return False

        if status >= 400:
            log.debug("Rolling back database session due to HTTP status: %r", status)
            return False

        log.debug("Committing database session; HTTP status: %r", status)
        return True

    def finish(self, environ):
        if self.session.transaction is not None:  # use getattr
            self.session.commit()
        self.session.close()

    def abort(self, environ):
        self.session.close()

    def populate_table(self, target, connection, **kw):  # pragma: no cover
        """Deprecated."""
        session = self._session()

        try:
            self.model.populate(session, target.name)
        except:  # pragma: no cover
            session.rollback()
            raise

        if session.transaction is not None:
            session.commit()
