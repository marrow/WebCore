# encoding: utf-8

""""""

from cmf.components.page.api    import IContentRenderer

from tw.forms                   import TextArea
from tw.wymeditor               import Wymeditor

__all__ = ['HTMLRenderer']


class HTMLRenderer(IContentRenderer):
    """A content renderer processes stored content and returns XHTML or a Genshi stream object."""
    
    mime = ("text/html")
    
    @property
    def editor(self):
        return [Wymeditor("content", attrs=dict(rows=15, cols=25), help_text="HTML content for the page.")]
    
    def render(self, controller, asset):
        """Return HTML or a Genshi XML stream."""
        
        return asset.content
