# encoding: utf-8

from cmf import release
from cmf.api import IComponent

class FolderComponent(IComponent):
    """"""
    
    title = "Folder"
    summary = "A generic container asset to group other assets logically."
    description = None
    icon = 'base-folder'
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
        from cmf.components.folder import model
        return dict([(i, getattr(model, i)) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.components.folder.controller import FolderController
        return FolderController
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        from cmf.components.folder.model import Folder
        return Folder(default="view:contents", **kw)
