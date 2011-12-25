#.encoding: utf-8


class CacheExtension(object):
    provides = ["cache"]
    
    def __init__(self, config):
        super(Extension, self).__init__()
    
    def start(self):
        """Executed during application startup just after binding the server."""
        pass # prepare the cache implementation (e.g. create folders, table, etc.)
    
    def stop(self):
        """Executed during web server shutdown, after unbinding."""
        pass # optionally clear the caches on shutdown
    
    def prepare(self, context):
        context.cache = CacheImplementation()
