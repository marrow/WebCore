# encoding: utf-8

"""Standard management interface for threading-sensitive database connections."""


class IManager(object):
    def __init__(self, application, model, **config):
        self.application, self.model, self.config = application, model, config.copy()
        self.uri = self.config.get('db.uri')
        
        self.connect()
    
    def connect(self):
        raise NotImplementedError("You must subclass IDBManager and implement this method yourself.")
    
    def resync(self):
        raise NotImplementedError("You must subclass IDBManager and implement this method yourself.")
    
    def flush(self):
        raise NotImplementedError("You must subclass IDBManager and implement this method yourself.")
    
    def start(self):
        raise NotImplementedError("You must subclass IDBManager and implement this method yourself.")
    
    def commit(self):
        raise NotImplementedError("You must subclass IDBManager and implement this method yourself.")
    
    def rollback(self):
        raise NotImplementedError("You must subclass IDBManager and implement this method yourself.")