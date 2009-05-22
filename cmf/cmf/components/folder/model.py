# encoding: utf-8

from elixir                 import using_options

from cmf.components.asset.model import Asset


log = __import__('logging').getLogger(__name__)
__all__ = ['Folder']
__model__ = ['Folder']


class Folder(Asset):
    """TODO:Docstring incomplete."""
    
    using_options(tablename='folders', inheritance='multi', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.components.folder.controller import FolderController
        return FolderController
    
    pass
