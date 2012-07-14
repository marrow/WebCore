#.encoding: utf-8


class CacheExtension(object):
    provides = ["cache"]
    
    def __init__(self, context):
        super(CacheExtension, self).__init__()
    
    def start(self, context):
        """Executed during application startup just after binding the server."""
        pass # prepare the cache implementation (e.g. create folders, table, etc.)
    
    def stop(self, context):
        """Executed during web server shutdown, after unbinding."""
        pass # optionally clear the caches on shutdown
    
    def prepare(self, context):
        # context.cache = CacheImplementation()
        pass
