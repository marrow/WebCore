# encoding: utf-8

from cmf.


class IFileProcessor(object):
    """A file processor method must return """
    
    def __init__(self, asset):
        self.asset = asset
    
    def scale(self, x=None, y=None, xy=None, square=False):
        """Return a JPEG stream or PIL Image instance for a thumbnail or preview at the given resolution."""
        raise NotImplementedError
    
    def embed(self, x=None, y=None, xy=None, square=False):
        """Return HTML or a Genshi XML stream to embed this file in the browser."""
        raise NotImplementedError