# encoding: utf-8

"""Exceptions handled by the abstract file processor API."""

__all__ = []


class ProcessorIncorrectFile(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message if isinstance(self.message, basestring) else repr(self.message)


class ProcessorNotThumbnailable(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message if isinstance(self.message, basestring) else repr(self.message)
    