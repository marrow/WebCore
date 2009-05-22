# encoding: utf-8

from cmf import release
from cmf.api import IComponent

class FileComponent(IComponent):
    """"""
    
    title = "File"
    summary = "An arbitrary uploaded file."
    description = None
    icon = 'base-file'
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
        from cmf.components.file import model
        return dict([(i, getattr(model, i)) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.components.file.controller import FileController
        return FileController
    
    def authorize(self, child):
        """A File is a pure leaf node; nothing can be placed within."""
        return False
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        from cmf.components.file.model import File
        return File(default="view:preview", **kw)
