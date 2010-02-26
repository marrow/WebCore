# encoding: utf-8

"""WebCore database middleware API."""


import re


__all__ = ['TransactionalMiddlewareInterface']
log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')



class TransactionalMiddlewareInterface(object):
    def __init__(self, application, prefix, model, session, **config):
        if not hasattr(self, 'config'):
            self.config = dict()
        
        self.application = application
        self.prefix = prefix
        self.model = model
        self.session = session
        
        self.config.update(config.copy())
        
        for i in ('db.%s.engine', 'db.%s.model', 'db.%s.session'):
            if (i % prefix) in self.config:
                del self.config[i % prefix]
        
        log.info("Connecting %s database to '%s'.", prefix, _safe_uri_replace.sub(r'\1://\2@', self.config.get('%s.url' % prefix)))
        
        self.setup()
        self.ready()
    
    
    def setup(self):
        """Called to configure and attach sessions, etc."""
        raise NotImplementedError
    
    def ready(self):
        """Called by the middleware after the middleware has been configured."""
        if hasattr(self.model, 'prepare') and hasattr(self.model.prepare, '__call__'):
            self.model.prepare()
    
    
    def begin(self, environ):
        """Called at the beginning of a request to prepare a transaction."""
        raise NotImplementedError
    
    def vote(self, environ, status):
        """Called to ask the middleware if the transaction is still valid."""
        raise NotImplementedError
    
    def finish(self, environ):
        """Called to commit a transaction.  Only called if the transaction is valid."""
        raise NotImplementedError
    
    def abort(self, environ):
        """Called if the vote failed."""
        raise NotImplementedError
    
    
    def __call__(self, environ, start_response):
        log.debug("Preparing database session.")
        
        self.begin(environ)
        
        status = []
        
        def local_start(stat_str, headers=[]):
            status.append(int(stat_str.split(' ')[0]))
            return start_response(stat_str, headers)
        
        try:
            result = self.application(environ, local_start)
        
        finally:
            if self.vote(environ, status[0] if status else None):
                self.finish(environ)
        
            else:
                self.abort(environ)
        
        return result
