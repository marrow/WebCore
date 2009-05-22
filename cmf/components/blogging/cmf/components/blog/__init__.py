# encoding: utf-8

from cmf                    import release
from cmf.api                import IComponent

class BlogComponent(IComponent):
    """"""
    
    title = "Blog"
    summary = "A collection of articles published in a reverse-chronological manner."
    description = None
    icon = 'base-blog'
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
        from cmf.components.blog import model
        return dict([(i, model.__dict__[i]) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.components.blog.controller import BlogController
        return BlogController
    
    def authorize(self, child):
        """Allow non-container types to be placed within."""
        
        from cmf.components.folder.controller import FolderController
        
        return not issubclass(child.controller, FolderController)
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        from cmf.components.blog.model import Blog
        return File(default="view:summaries", **kw)