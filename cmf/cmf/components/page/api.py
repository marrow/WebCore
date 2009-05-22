# encoding: utf-8

"""An abstracted interface for generalized processing of textual content."""

__all__ = ['IContentRenderer']


class IContentRenderer(object):
    """A content renderer processes stored content and returns XHTML or a Genshi stream object."""
    
    extension = ""
    mime = None
    
    def __init__(self, asset):
        pass
    
    @property
    def editor(self):
        raise NotImplementedError
    
    def render(self, controller, asset):
        """Return HTML or a Genshi XML stream."""
        raise NotImplementedError