# encoding: utf-8

"""

Base asset controller.

"""

from tg                     import request, session, expose, flash, redirect, url
from pylons.i18n            import ugettext as _
from datetime               import datetime

from cmf.core               import View

from cmf.components.page.model          import Page
from cmf.components.folder.controller   import FolderController


log = __import__('logging').getLogger(__name__)
__all__ = ['KnowledgebaseController']



class KnowledgebaseController(FolderController):
    """TODO: Docstring incomplete."""
    
    browse          = View("Browse", "Browse answers.", 'base-page')
    search          = View("Search", "Search for a solution.", 'base-page')
    
    @expose('genshi:cmf.components.knowledgebase.views.browser')
    def _view_browse(self):
        assets = Page.query.filter(Page.l >= self.asset.l).filter(Page.r <= self.asset.r)
        
        return dict(controller=self, asset=self.asset, assets=assets)
    
    @expose('genshi:cmf.components.knowledgebase.views.search')
    def _view_search(self, category=None, query=None):
        return dict(controller=self, asset=self.asset)
    