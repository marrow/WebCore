# encoding: utf-8

from cmf                    import release
from cmf.api                import IComponent

class AccountComponent(IComponent):
    """"""
    
    title = "Account"
    summary = "An asset representing a user capable of logging in."
    description = None
    icon = 'base-account'
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
        from cmf.components.account import model
        return dict([(i, model.__dict__[i]) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.components.account.controller import AccountController
        return AccountController