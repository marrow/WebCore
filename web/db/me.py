# encoding: utf-8

"""MongoEngine database adapter."""

import re
import warnings
import mongoengine

from marrow.util.object import load_object


__all__ = ['MongoEngineMiddleware']
log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


def MongoEngineMiddleware(application, prefix, model, session=None, **config):
    url = config.get('%s.url' % (prefix,), 'mongo://localhost')

    log.info("Connecting MongoEngine to '%s'.", _safe_uri_replace.sub(r'\1://\2@', url))

    connection = dict(tz_aware=True)

    scheme, parts = url.split('://', 1)
    parts, db = parts.split('/', 1)
    auth, host = parts.split('@', 1) if '@' in parts else (None, parts)

    if scheme != 'mongo':
        raise Exception('The URL must begin with \'mongo://\'!')

    connection['host'], connection['port'] = host.split(':') if ':' in host else (host, '27017')
    connection['port'] = int(connection['port'])

    if auth:  # pragma: no cover
        connection['username'], _, connection['password'] = auth.partition(':')

    log.debug("Connecting to %s database with connection information: %r", db, connection)
    model.__dict__['connection'] = mongoengine.connect(db, **connection)

    prepare = getattr(model, 'prepare', None)
    if hasattr(prepare, '__call__'):
        warnings.warn("Use of the hard-coded 'prepare' callback is deprecated.\n"
                "Use the 'ready' callback instead.", DeprecationWarning)
        prepare()

    cb = config.get(prefix + '.ready', None)

    if cb is not None:
        cb = load_object(cb) if isinstance(cb, basestring) else cb

        if hasattr(cb, '__call__'):
            cb()

    return application
