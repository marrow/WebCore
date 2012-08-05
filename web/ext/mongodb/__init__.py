# encoding: utf-8
from __future__ import unicode_literals, division, print_function, absolute_import

from marrow.util.compat import basestring

try:
    from pymongo import Connection
except ImportError:
    raise ImportError('You need to install pymongo to use this extension')


class MongoDBExtension(object):
    provides = ['mongodb', 'database']

    def __init__(self, context, contextvar='mongodb', connection=None, **conn_params):
        super(MongoDBExtension, self).__init__()

        if not isinstance(contextvar, basestring):
            raise TypeError('The "contextvar" option needs to be a string')
        if connection is not None and not isinstance(connection, Connection):
            raise TypeError('The "connection" option needs to be a Connection')

        self._contextvar = contextvar
        self._conn_params = conn_params
        self._connection = connection

    def start(self, context):
        # Attempt to connect to the server
        if self._connection is not None:
            self._connection = Connection(**self._conn_params)

        # Add the connection to the context
        if hasattr(context, self._contextvar):
            raise Exception('The context already has a variable named "%s"' % self._contextvar)
        setattr(context, self._contextvar, self._connection)
