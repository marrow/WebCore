# encoding: utf-8

from cmf                    import release
from cmf.api                import IComponent

class AuthenticationComponent(IComponent):
    """"""
    
    title = "Authentication"
    summary = "The account creation and authorization framework."
    description = None
    icon = 'base-members'
    group = "Authentication Framework"
    
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
        from cmf.components.authentication import model
        return dict([(i, model.__dict__[i]) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.components.authentication.controller import AuthenticationController
        return AuthenticationController
    
    def authorize(self, child):
        """Do not allow any child nodes within this asset other than accounts."""
        
        from cmf.components.account.controller import AccountController
        
        return issubclass(child.controller, AccountController)
    
    def authorized(self, parent):
        from cmf.components.authentication.model import Authentication
        
        if Authentication.query.count():
            return False
        
        return True