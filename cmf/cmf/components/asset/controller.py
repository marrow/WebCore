# encoding: utf-8

"""

Base asset controller.

"""

import                      logging, re, md5

from tg                     import request, session, expose, flash, redirect, url
from pylons.i18n            import ugettext as _
from datetime               import datetime

from cmf.core               import components, action, view, Action, View, AuthenticatedAction, AuthenticatedView, OwnerAction, OwnerView
from cmf.util               import normalize, yield_property
from cmf.components.core    import BaseController

from cmf.components.asset.core import CoreMethods


log = logging.getLogger(__name__)
__all__ = ['AssetController']


class AssetController(BaseController):
    """"""
    
    __repr__        = lambda self: '%s %s (%s %r)' % (self.__class__.__name__, self.asset.guid, self.asset.name, self.asset.title)
    
    # TODO: Deprecated.
    contents        = AuthenticatedView("Contents", "View a list of assets contained within this asset.", 'base-folder')
    remove          = OwnerAction("Remove", "Remove this asset (and its contents) from the site.", 'base-delete')
    security        = OwnerAction("Security", "Modify permissions and security for this asset.", 'base-security')
    properties      = OwnerAction("Properties", "Modify behind-the-scenes information about this asset.", 'base-properties')
    
    
    def __init__(self, guid=None):
        super(AssetController, self).__init__(guid)
        self._api_core = CoreMethods(self)
    
    
    @expose('genshi:cmf.components.asset.views.contents')
    @view(AuthenticatedView, 'Contents', "View a list of assets contained within this asset.", icon='base-asset')
    def _view_contents(self):
        return dict()
        return dict(controller=self, asset=self.asset)
    
    
    @expose('genshi:cmf.components.asset.views.create')
    @action(AuthenticatedAction, "Create", "Create new assets.", icon='base-create')
    def _action_create(self, **kw):
        if 'cmf.authentication.account' not in session:
            flash("You do not have sufficient priveledges to create assets here.", 'error')
            session['cmf.authentication.target.asset'] = self.asset.guid
            session['cmf.authentication.target'] = self.asset.path_info
            session.save()
            redirect('/action:authenticate')
        
        if 'name' in kw:
            from cmf.components.asset.model import session as DBSession, Tag
            
            try:
                if 'name' not in kw or not kw['name']:
                    kw['name'] = normalize(kw['title'], yield_property(self.asset.children, 'name'))
                else: kw['name'] = normalize(kw['name'], yield_property(self.asset.children, 'name'))
                
                log.debug("Creating asset of kind %r: %r", components[kw['kind']], kw)
                
                kw['owner_guid'] = session['cmf.authentication.account'].id
                
                tags = None
                if 'tags' in kw:
                    tags = kw['tags']
                    del kw['tags']
                
                asset = components[kw['kind']].constructor(**kw)
                
                self.asset.attach(asset, after=kw['direction'] == 'after')
                
                if tags:
                    asset.tags.extend(Tag.split(tags))
            
            except:
                DBSession.rollback()
                log.exception("Error creating asset.")
            
            else:
                DBSession.commit()
                redirect(asset.path + '/action:modify')
        
        from itertools import groupby
        
        component = None
        for i in components.itervalues():
            if isinstance(self, i.controller):
                component = i
                break
        if not component: log.error("Unable to find component for %r!", self)
        
        tmp = [(j.group, i, j) for i, j in components.iteritems()]
        tmp.sort()
        
        kinds = []
        for k, g in groupby(tmp, lambda i: i[0]):
            kinds.append((k, [(i, j) for x, i, j in g if j.authorized(self.asset) and component.authorize(j)]))
        
        log.debug("Kinds: %r", kinds)
        
        return dict(kinds=kinds)
    
    
    @expose()
    @action(OwnerAction, "Remove", "Delete this asset and all descendants.", icon='base-delete')
    def _action_remove(self):
        import model
        
        parent = self.asset.parent
        l, r = self.asset.l, self.asset.r
        self.asset.delete()
        model.session.commit()
        model.Asset.stargate(model.Asset.l > l, model.Asset.r > r, -(r - l + 1))
        
        flash("success::Successfully Deleted Asset::Succesfully removed asset.")
        redirect(url(parent.path + '/'))
    
    
    @expose('genshi:cmf.components.asset.views.properties')
    @action(OwnerAction, "Properties", "Modify behind-the-scenes information about this asset", icon='base-properties')
    def _action_properties(self, **kw):
        from cmf.components.asset.model import Tag
        from elixir import session as DBSession
        
        if 'name' in kw:
            self.asset.modified = datetime.now()
            
            for i, j in kw.iteritems():
                if i in ['name', 'default']:
                    setattr(self.asset, i, j)
                
                elif i == 'tags':
                    del self.asset.tags[:]
                    self.asset.tags.extend(Tag.split(kw['tags']))
                
                elif i in ['published', 'retracted']:
                    try:
                        from tw.forms.validators import DateTimeConverter
                        setattr(self.asset, i, DateTimeConverter().to_python(j.strip()) if j.strip() else None)
                        
                    except:
                        log.exception("Invalid date given, date dropped.")
                        pass
            
            DBSession.commit()
            
            flash("Changes made successfully.", 'success')
            redirect(self.asset.path + '/')
        
        return dict()
    
    
    @expose('genshi:cmf.components.asset.views.security')
    @action(OwnerAction, "Security", "Modify permissions and other security settings for this asset.", icon='base-security')
    def _action_security(self, **kw):
        import model
        
        if kw.get('action', None) == "save":
            if kw.get('guest', False):
                if kw.get('password', None):
                    self.asset.properties['cmf.authentication.guestpass'] = md5.md5(kw['password']).hexdigest()
                    flash("success::Saved Changes::Successfully updated guest pass.")
            
            elif 'cmf.authentication.guestpass' in self.asset.properties:
                del self.asset.properties['cmf.authentication.guestpass']
                flash("success::Saved Changes::Successfully removed guest pass.")
            
            model.session.commit()
            
            redirect(self.asset.path + '/')
        
        return dict()
    
    
