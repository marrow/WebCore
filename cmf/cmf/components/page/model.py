# encoding: utf-8

import                      logging
from elixir                 import using_options, Field, String, UnicodeText

# from cmf.components.page.controller import PageController

from cmf.components.asset.model import Asset


log = logging.getLogger(__name__)
__all__ = ['Page']
__model__ = ['Page']


class Page(Asset):
    """TODO:Docstring incomplete."""
    
    using_options(tablename='pages', inheritance='multi', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.components.page.controller import PageController
        return PageController
    
    content         = Field(UnicodeText, deferred=True)
    renderer        = Field(String(100), default="html") # plain, html, safe-html, rest, etc.
