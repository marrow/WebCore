# encoding: utf-8

""""""

from cmf.components.page.api    import IContentRenderer

from tg                         import request, session
from tw.forms                   import TextArea

from genshi                     import XML, HTML
from genshi.filters             import HTMLSanitizer
from genshi.template            import MarkupTemplate


log = __import__('logging').getLogger(__name__)
__all__ = ['GenshiRenderer']


class GenshiRenderer(IContentRenderer):
    """A content renderer processes stored content and returns XHTML or a Genshi stream object."""
    
    extension = ".html"
    mime = ("text/html", "application/xhtml+xml")
    
    @property
    def editor(self):
        return [TextArea("content", attrs=dict(rows=15, cols=25), help_text="Valid XHTML content for the page.")]
    
    def render(self, controller, asset):
        """Return HTML or a Genshi XML stream."""
        def generate():
            content = u"""<div xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/">%s</div>""" % (asset.content, )
            
            try:
                stream = XML(content)
                template = MarkupTemplate(stream) # , allow_exec=False
                stream = template.generate(
                        asset = asset,
                        controller = controller,
                        request = request,
                        session = session
                    )# | HTMLSanitizer()
                content = stream.render(encoding=None)
                
            except:
                # We probably have bad HTML.  Pity.  No templating for you!
                log.exception("%r Exception attempting to evaluate template.", asset)
                stream = HTML(content)# | HTMLSanitizer()
                content = stream.render(encoding=None)
            
            return content
        
        return generate()
