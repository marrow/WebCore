# encoding: utf-8

from cmf                    import release
from cmf.api                import IComponent


__all__ = ['AssetComponent', 'controller', 'core', 'model', 'views']


class AssetComponent(IComponent):
    """"""
    
    title = "Asset"
    summary = None
    description = None
    icon = 'base-asset'
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
        from cmf.components.asset import model
        return dict([(i, getattr(model, i)) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.components.asset.controller import AssetController
        return AssetController
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        from cmf.components.asset.model import Asset
        return Asset(default="view:contents", **kw)
    
    def authorized(self, parent):
        return False