# encoding: utf-8

""""""

from cmf.components.page.api    import IContentRenderer

from tw.forms                   import TextArea

__all__ = ['RawRenderer']


class RawRenderer(IContentRenderer):
    """A content renderer processes stored content and returns XHTML or a Genshi stream object."""
    
    @property
    def editor(self):
        return [TextArea("content", attrs=dict(rows=15, cols=25), help_text="Valid XHTML content for the page.")]
    
    def render(self, controller, asset):
        """Return HTML or a Genshi XML stream."""
        
        return asset.content
