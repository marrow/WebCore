# encoding: utf-8

from cmf                    import release
from cmf.api                import IComponent

class KnowledgebaseComponent(IComponent):
    """"""
    
    title = "Knowledgebase"
    summary = "A searchable collection of solutions."
    description = None
    icon = 'base-kb'
    group = "Advanced Types"
    
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
        from cmf.components.knowledgebase import model
        return dict([(i, model.__dict__[i]) for i in model.__model__])
    
    @property
    def controller(self):
        from cmf.components.knowledgebase.controller import KnowledgebaseController
        return KnowledgebaseController
