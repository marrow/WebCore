from pymongo import Connection


class MongoDBExtension(object):
    def __init__(self, context, connection, **conn_params):
        super(MongoDBExtension, self).__init__()
        self._connection_ref = connection
        self._conn_params = conn_params

    def start(self, context):
        # Attempt to connect to the server
        self._connection = Connection(**self._conn_params)

        # Set the "connection" attribute in the given module
        module_ref, _, variable_ref = self._connection.split(':')
        module = __import__(module_ref)
        setattr(module, variable_ref, self._connection)
