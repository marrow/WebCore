# encoding: utf-8

import                      logging
from elixir                 import using_options # , Field, String, UnicodeText, Boolean

from cmf.components.asset.model import Asset


log = logging.getLogger(__name__)
__all__ = ['Authentication']
__model__ = ['Authentication']


class Authentication(Asset):
    """TODO:Docstring incomplete."""
    
    using_options(tablename='authentication', inheritance='multi', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.components.authentication.controller import AuthenticationController
        return AuthenticationController
    
    pass