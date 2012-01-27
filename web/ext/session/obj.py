# encoding: utf-8

from marrow.util.bunch import Bunch


class Session(Bunch):
    def __init__(self, identifier):
        self._loaded = False
    
    def save(self):
        """Ensure the session is saved before continuing."""
        pass
    
    def delete(self):
        """The current session should be deleted. No further session access is possible."""
        pass
    
    def invalidate(self):
        """The current session should be deleted and a new session begun."""
        pass
    
    @property
    def id(self):
        pass
    
    @property
    def loaded(self):
        pass
    
    @property
    def locked(self):
        pass




