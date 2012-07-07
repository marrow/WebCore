# encoding: utf-8

"""WebCore database middleware API."""

from webob.exc import HTTPException

import warnings
import re


__all__ = ['TransactionalMiddlewareInterface']
log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


class TransactionalMiddlewareInterface(object):
    def __init__(self, application, prefix, model, session, **config):
        self.config = config

        self.application = application
        self.prefix = prefix
        self.model = model
        self.session = session

        log.info("Connecting %s database to '%s'.", prefix, _safe_uri_replace.sub(r'\1://\2@', self.config.get('%s.url' % prefix)))

        self.setup()
        self.ready()

    def setup(self):  # pragma: no cover
        """Called to configure and attach sessions, etc."""
        raise NotImplementedError

    def ready(self):
        """Called by the middleware after the middleware has been configured."""
        if hasattr(self.model, 'prepare') and hasattr(self.model.prepare, '__call__'):
            warnings.warn("Use of the hard-coded 'prepare' callback is deprecated.\n"
                    "Use the 'ready' callback instead.", DeprecationWarning)
            self.model.prepare()

    def begin(self, environ):  # pragma: no cover
        """Called at the beginning of a request to prepare a transaction."""
        raise NotImplementedError

    def vote(self, environ, status):  # pragma: no cover
        """Called to ask the middleware if the transaction is still valid."""
        raise NotImplementedError

    def finish(self, environ):  # pragma: no cover
        """Called to commit a transaction.  Only called if the transaction is valid."""
        raise NotImplementedError

    def abort(self, environ):  # pragma: no cover
        """Called if the vote failed."""
        raise NotImplementedError

    def __call__(self, environ, start_response):
        log.debug("Preparing database session.")

        self.begin(environ)

        result = None
        status = []
        exc = []

        def local_start(stat_str, headers=[], exc_info=None):
            status.append(int(stat_str.split(' ')[0]))
            if exc_info:
                exc.append(exc_info)
            return start_response(stat_str, headers, exc_info)

        try:
            result = self.application(environ, local_start)
        except HTTPException:
            pass
        except Exception as e:
            exc.append(e)

        if self.vote(environ, status[0] if status else None, exc[0] if exc else None):
            self.finish(environ)
        else:
            self.abort(environ)

        return result
