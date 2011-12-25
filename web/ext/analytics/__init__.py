# encoding: utf-8

import time


class AnalyticsExtension(object):
    uses = ['db']
    provides = ['analytics']
    
    def __init__(self, config):
        """Executed to configure the extension."""
        super(AnalyticsExtension, self).__init__()
        # create storage back-end
    
    def start(self):
        """Executed during application startup just after binding the server."""
        pass # tell storage engine to prepare
        # notify engine of startup
    
    def stop(self):
        """Executed during application shutdown after the last request has been served."""
        pass # notify engine of shutdown
    
    def prepare(self, context):
        """Executed during request set-up."""
        context._start_time = None
        pass # what should we publish?
    
    def before(self, context):
        """Executed after all extension prepare methods have been called, prior to dispatch."""
        context._start_time = time.time()
    
    def after(self, context, exc=None):
        """Executed after dispatch has returned and the response populated, prior to anything being sent to the client."""
        pass # notify engine of request completion
