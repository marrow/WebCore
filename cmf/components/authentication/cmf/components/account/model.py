# encoding: utf-8

import                      hashlib
from elixir                 import using_options, Field, String, Unicode

from cmf.components.asset.model import Asset


log = __import__('logging').getLogger(__name__)
__all__ = ['Account']
__model__ = ['Account']


class Account(Asset):
    """TODO:Docstring incomplete."""
    
    using_options(tablename='accounts', inheritance='multi', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.components.account.controller import AccountController
        return AccountController
    
    email                 = Field(Unicode(200))
    _password             = Field(String(64), colname="password", deferred=True)
    
    def set_password(self, value):
        self._password = hashlib.md5(value).hexdigest()
    
    password = property(lambda self: None, set_password)
