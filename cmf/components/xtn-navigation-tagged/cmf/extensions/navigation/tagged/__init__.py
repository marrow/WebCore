# encoding: utf-8

from cmf.api                                    import IComponent
from cmf.extensions.navigation.tagged           import release


class TaggedNavigationComponent(IComponent):
    title = "Tagged Navigation"
    summary = release.summary
    description = release.description
    icon = 'base-extension'
    group = "Extensions: Navigation"
    
    version = release.version
    author = release.author
    email = release.email
    url = release.url
    copyright = release.copyright
    license = release.license
    
    enabled = True
    # model = 'cmf.extensions.navigation.tagged.model'
    # controller = 'cmf.extensions.navigation.tagged.controller:TaggedNavigationControlle'
    
    @property
    def model(self):
        from cmf.extensions.navigation.tagged import model
        return dict([(i, getattr(model, i)) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.extensions.navigation.tagged.controller import TaggedNavigationController
        return TaggedNavigationController
    
    def authorized(self, parent):
        """Standard singleton behavior."""
        
        from cmf.extensions.navigation.tagged.model import TaggedNavigation
        return not TaggedNavigation.query.count()
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        
        from cmf.extensions.navigation.tagged.model import TaggedNavigation
        return TaggedNavigation(default="view:contents", **kw)