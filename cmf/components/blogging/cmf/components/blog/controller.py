# encoding: utf-8

"""

Blog controller.

"""

from tg                     import request, session, expose, flash, redirect, url
from pylons.i18n            import ugettext as _
from datetime               import datetime

from cmf.core               import view, action, View, OwnerAction

from cmf.components.asset.model         import Asset, Tag
from cmf.components.folder.controller   import FolderController

from sqlalchemy import func, or_, and_


log = __import__('logging').getLogger(__name__)
__all__ = ['BlogController']



class BlogController(FolderController):
    """TODO: Docstring incomplete."""
    
    summaries       = View("Summaries", "Browse summaries.", 'base-blog-summaries')
    
    @expose('genshi:cmf.components.blog.views.summaries')
    @view(View, "Tag Search", "Search for entries by tag.", icon='base-blog-tags')
    def tags(self, tag):
        assets = self.asset.children
        
        assets = assets.filter(Asset._tags.any(name=tag))
        
        # Display only published items that have not been withdrawn.
        #assets = assets.filter(and_(
        #        Asset.published <= datetime.now(),
        #        or_(Asset.retracted == None, Asset.retracted >= datetime.now())
        #    ))
        
        # if self.asset.days: pass # Filter by date range.  (self.show in days)
        
        # TODO: This needs to be cleaned up.  Pretty sure it won't work properly for all cases.
        if self.asset.refresh: order = func.if_(Asset.modified > Asset.published, Asset.modified, Asset.published)
        else: order = func.if_(Asset.published > Asset.created, Asset.published, Asset.created)
        
        assets = assets.order_by(order.desc())
        
        if not self.asset.days: assets = assets.limit(self.asset.show)
        
        return dict(assets=assets)
    
    @expose('genshi:cmf.components.blog.views.summaries')
    @view(View, "Summaries", "Browse summaries.", icon='base-blog-summaries') # , cache=86400, scope='children') -- generates 'can not pickle function objects' error
    def _view_summaries(self):
        # Programatically adjust the sorting by user options. Speicifcally should updated items filter to the top again?
        
        assets = self.asset.children
        
        # Display only published items that have not been withdrawn.
        #assets = assets.filter(and_(
        #        Asset.published <= datetime.now(),
        #        or_(Asset.retracted == None, Asset.retracted >= datetime.now())
        #    ))
        
        # if self.asset.days: pass # Filter by date range.  (self.show in days)
        
        # TODO: This needs to be cleaned up.  Pretty sure it won't work properly for all cases.
        if self.asset.refresh: order = func.if_(Asset.modified > Asset.published, Asset.modified, Asset.published)
        else: order = func.if_(Asset.published > Asset.created, Asset.published, Asset.created)
        
        assets = assets.order_by(order.desc())
        
        if not self.asset.days: assets = assets.limit(self.asset.show)
        
        return dict(assets=assets)
