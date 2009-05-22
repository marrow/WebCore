# encoding: utf-8

from cmf.api                                    import IComponent
from cmf.extensions.breadcrumb                  import release


class BreadcrumbComponent(IComponent):
    title = "Breadcrumb List"
    summary = release.summary
    description = release.description
    icon = 'base-extension'
    group = "Extensions: Cosmetic"
    
    version = release.version
    author = release.author
    email = release.email
    url = release.url
    copyright = release.copyright
    license = release.license
    
    enabled = True
    # model = 'cmf.extensions.breadcrumb.model'
    # controller = 'cmf.extensions.breadcrumb.controller:BreadcrumbController'
    
    @property
    def model(self):
        from cmf.extensions.breadcrumb import model
        return dict([(i, getattr(model, i)) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.extensions.breadcrumb.controller import BreadcrumbController
        return BreadcrumbController
    
    def authorized(self, parent):
        """Standard singleton behavior."""
        
        from cmf.extensions.breadcrumb.model import Breadcrumb
        return not Breadcrumb.query.count()
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        
        from cmf.extensions.breadcrumb.model import Breadcrumb
        return Breadcrumb(default="view:contents", **kw)