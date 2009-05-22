# encoding: utf-8

from cmf                    import release
from cmf.api                import IComponent

class ExtensionComponent(IComponent):
    """"""
    
    title = "Extension"
    summary = None
    description = None
    icon = 'base-extension'
    
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
        from cmf.components.extension import model
        return dict([(i, getattr(model, i)) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.components.extension.controller import Extension
        return Extension
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        from cmf.components.extension.model import Extension
        return Extension(default="view:contents", **kw)
    
    def authorized(self, parent):
        return False