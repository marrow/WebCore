# encoding: utf-8

from cmf                    import release
from cmf.api                import IComponent

class PageComponent(IComponent):
    """"""
    
    title = "Page"
    summary = "Textual content."
    description = None
    icon = 'base-page'
    group = "Basic Types"
    
    version = release.version
    author = release.author
    email = release.email
    url = release.url
    copyright = release.copyright
    license = release.license
    
    @property
    def enabled(self):
        return True
    
    @property
    def model(self):
        import cmf.components.page.model as model
        return dict([(i, getattr(model, i)) for i in model.__model__])
    
    @property
    def controller(self):
        import cmf.components.page.controller as controller
        return controller.PageController
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        from cmf.components.page.model import Page
        return Page(default="view:render", **kw)
