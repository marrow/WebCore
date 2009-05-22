# encoding: utf-8

from cmf.api                                    import IComponent
from cmf.extensions.analytics.google            import release


class GoogleAnalyticsComponent(IComponent):
    title = "Google Analytics"
    summary = release.summary
    description = release.description
    icon = 'base-extension'
    group = "Extensions: Analytics"
    
    version = release.version
    author = release.author
    email = release.email
    url = release.url
    copyright = release.copyright
    license = release.license
    
    enabled = True
    # model = 'cmf.extensions.analytics.google.model'
    # controller = 'cmf.extensions.analytics.google.controller:GoogleAnalyticsController'
    
    @property
    def model(self):
        from cmf.extensions.analytics.google import model
        return dict([(i, getattr(model, i)) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.extensions.analytics.google.controller import GoogleAnalyticsController
        return GoogleAnalyticsController
    
    def authorized(self, parent):
        """Standard singleton behavior."""
        
        from cmf.extensions.analytics.google.model import GoogleAnalytics
        return not GoogleAnalytics.query.count()
    
    def constructor(self, **kw):
        """A factory method to create new instances of this component."""
        from cmf.extensions.analytics.google.model import GoogleAnalytics
        return GoogleAnalytics(default="view:contents", **kw)