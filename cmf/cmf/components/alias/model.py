# encoding: utf-8

from elixir                 import using_options

from cmf.components.asset.model import Asset


log = __import__('logging').getLogger(__name__)
__all__ = ['Folder']
__model__ = ['Folder']


class Alias(Asset):
    """TODO:Docstring incomplete."""
    
    using_options(tablename='aliases', inheritance='multi', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.components.alias.controller import AliasController
        return AliasController
    
    target = Field(String(250))
