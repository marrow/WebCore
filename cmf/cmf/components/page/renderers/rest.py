# encoding: utf-8

""""""

from cmf.components.page.api    import IContentRenderer

from tw.forms                   import TextArea
from docutils.core              import publish_parts

__all__ = ['RestRenderer']


class RestRenderer(IContentRenderer):
    """A content renderer processes stored content and returns XHTML or a Genshi stream object."""
    
    extension = ".rst"
    mime = "text/x-rst"
    
    @property
    def editor(self):
        return [TextArea("content", attrs=dict(rows=15, cols=25), help_text="Restructured Text content for the page.")]
    
    def render(self, controller, asset):
        """Return HTML or a Genshi XML stream."""
        def generate():
            return publish_parts(self.asset.content, writer_name="html", settings_overrides=dict(initial_header_level=2))['html_body']
        
        return generate()
