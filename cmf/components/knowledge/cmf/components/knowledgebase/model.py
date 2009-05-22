# encoding: utf-8

from elixir                 import using_options

from cmf.components.folder.model import Folder


log = __import__('logging').getLogger(__name__)
__all__ = ['Knowledgebase']
__model__ = ['Knowledgebase']


class Knowledgebase(Folder):
    """TODO:Docstring incomplete."""
    
    using_options(tablename='knowledgebases', inheritance='multi', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.components.knowledgebase.controller import KnowledgebaseController
        return KnowledgebaseController
    
    pass
