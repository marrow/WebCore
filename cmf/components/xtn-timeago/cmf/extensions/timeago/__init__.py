# encoding: utf-8

from cmf.api                                    import IComponent
from cmf.extensions.timeago                     import release


class TimeAgoComponent(IComponent):
    title = "Relative Time Extension"
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
    # model = 'cmf.extensions.timeago.model'
    # controller = 'cmf.extensions.timeago.controller:TimeAgoController'
    
    @property
    def model(self):
        from cmf.extensions.timeago import model
        return dict([(i, getattr(model, i)) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.extensions.timeago.controller import TimeAgoController
        return TimeAgoController
    
    def authorized(self, parent):
        """Standard singleton behavior."""
        
        from cmf.extensions.timeago.model import TimeAgo
        return not TimeAgo.query.count()
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        
        from cmf.extensions.timeago.model import TimeAgo
        return TimeAgo(default="view:contents", **kw)