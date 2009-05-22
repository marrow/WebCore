# encoding: utf-8

from cmf import release
from cmf.api import IComponent

class AliasComponent(IComponent):
    """"""
    
    title = "Alias"
    summary = "Redirect old URLs to new URLs to prevent bookmark failure."
    description = None
    icon = 'base-alias'
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
        from cmf.components.alias import model
        return dict([(i, getattr(model, i)) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.components.alias.controller import AliasController
        return AliasController
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        from cmf.components.alias.model import Alias
        return Alias(default="view:default", **kw)
    
    def allow(self, child):
        return False