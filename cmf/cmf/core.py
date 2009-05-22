# encoding: utf-8

"""

Base asset controller.

"""

import                      pkg_resources, tg

from cmf.api                import IAction, IView
from cmf.hooks              import GlobalHooks
from cmf.util               import AttrDict

from tg                     import tmpl_context, session

try:
    from tg.util                import DottedFileNameFinder

except:
    from tg.util                import get_dotted_filename as gdf
    
    class DottedFileNameFinder(object):
        cache = {}
        
        def get_dotted_filename(self, path):
            if path not in self.cache: self.cache[path] = gdf(path)
            return self.cache[path]


log = __import__('logging').getLogger(__name__)
__all__ = ['config', 'components', 'namespace', 'start', 'Action', 'View', 'AuthenticatedMixIn', 'AuthenticatedAction', 'AuthenticatedView', 'OwnerMixIn', 'OwnerAction', 'OwnerView', 'AnonymousMixIn', 'AnonymousAction', 'AnonymousView', 'view', 'action']


config = AttrDict()
components = AttrDict()
namespace = AttrDict()
dotted = DottedFileNameFinder()


def start(cfg=AttrDict(), **kw):
    if components: return
    
    log.info("TurboCMF initializing.")
    
    config.update(cfg)
    config.update(kw)
    
    namespace.master = [dotted.get_dotted_filename(config.master)] if config.get('master', None) else []
    
    for res in pkg_resources.iter_entry_points('turbocmf.component'):
        try:
            instance = res.load()()
        
        except:
            log.exception("Error scanning available CMF components.  CMF unavailable.")
            return
        
        try:
            if instance.enabled:
                instance.start()
                components[res.name] = instance
        
        except:
            log.exception("Error initializing CMF component %r.", instance)
            continue
    
    log.info("Loaded CMF components: %s", ', '.join([i.title for i in components.itervalues()]))
    
    log.info("TurboCMF ready.")


class Action(IAction):
    pass


class View(IView):
    pass


class AuthenticatedMixIn(object):
    def authorized(self, asset):
        # log.debug("AuthenticatedMixIn authorization: %r", session.get('cmf.authentication.account', None))
        if 'cmf.authentication.account' in session and session['cmf.authentication.account']:
            return True
        
        return False

class AuthenticatedAction(AuthenticatedMixIn, IAction):
    pass

class AuthenticatedView(AuthenticatedMixIn, IView):
    pass


class OwnerMixIn(object):
    def authorized(self, asset):
        # log.debug("OwnerMixIn authorization: %r == %r", session.get('cmf.authentication.account', None), asset.owner)
        if 'cmf.authentication.account' in session and asset.owner and asset.owner.id == session['cmf.authentication.account'].id:
            return True
        
        return False

class OwnerAction(OwnerMixIn, IAction):
    pass

class OwnerView(OwnerMixIn, IView):
    pass


class AnonymousMixIn(object):
    def authorized(self, asset):
        # log.debug("AnonymousMixIn authorization: %r", session.get('cmf.authentication.account', None))
        if 'cmf.authentication.account' not in session or not session['cmf.authentication.account']:
            return True

        return False

class AnonymousAction(AnonymousMixIn, IAction):
    pass

class AnonymousView(AnonymousMixIn, IView):
    pass


def process(controller):
    from datetime import datetime
    from cmf.components.asset.model import Asset
    from cmf.components.extension.model import Extension
    from sqlalchemy import func, or_, and_
    
    cmf_namespace = AttrDict(namespace)
    cmf_namespace.root = Asset.query.filter_by(l=1).one()
    cmf_namespace.flash = AttrDict(dict(status=tg.get_status(), message=tg.get_flash())) if tg.get_flash() else AttrDict()
    
    # TODO: Iterate through all active Extensions and let them do their magic.
    for extension in Extension.query.filter(Extension.published <= datetime.now()): # and_(, or_(Extension.retracted == None, Extension.retracted >= datetime.now()))).all():
        log.debug("Processing extension %r for request.", extension)
        ec = extension.controller
        
        if hasattr(ec, 'namespace'):
            log.debug("Extension has namespace components.")
            cmf_namespace.update(ec.namespace)
        
        if hasattr(ec, 'inject'):
            log.debug("Extension has ToscaWidgets injection components.")
            ec.inject(controller)
        
        if hasattr(ec, 'template'):
            log.debug("Extension has Genshi template components.")
            if not isinstance(cmf_namespace.master, list): cmf_namespace.master = [cmf_namespace.master]
            if dotted.get_dotted_filename(ec.template) not in cmf_namespace.master: cmf_namespace.master.append(dotted.get_dotted_filename(ec.template))
    
    return cmf_namespace


def view(cls, name, description=None, icon=None, cache=None, scope="asset"):
    """Mark a method as a view.
    
    Pass the decorator the short name (used for path construction), description, and a few optional values:
    
    `icon` -- An icon to represent this view in pretty lists.
    `cache` -- If present the result of the view is memoized and cached for the given time period given in seconds, or until the underlying asset is updated.
    `scope` -- How deep to search for updates.  Used to invalidate the cache if the view aggregates children and one is updated, for example.  Values can be 'asset' (default), 'children', or 'descendants'.
    """
    
    # log.debug("%r view decorator initialized.  [%r, %r, icon=%r, cache=%r, scope=%r]", cls, name, description, icon, cache, scope)
    
    def decorator(fn):
        from datetime import datetime
        from cmf.components.asset.model import Asset
        from cmf.components.extension.model import Extension
        from sqlalchemy import func, or_, and_
        
        fn.action = cls(name, description, icon)
        
        def wrapper(self, *args, **kw):
            cmf_namespace = process(self)
            
            if cache:
                from pylons import cache as cache_factory
                viewcache = cache_factory.get_cache('cmf.cache.views', type="file")
                
                # Determine the latest creation/modification time.
                # TODO: Otptimize this to return a single value from the query rather than an object.
                if scope == "asset":
                    latest = max([self.asset.modified if self.asset.modified else datetime(1984, 9, 21), self.asset.created if self.asset.created else datetime(1984, 9, 21)])
                    
                else:
                    latest = getattr(self.asset, scope)
                    latest = latest.order_by(func.if_(Asset.modified > Asset.created, Asset.modified, Asset.created).desc()).first()
                    latest = max([latest.modified if latest.modified else datetime(1984, 9, 21), latest.created if latest.created else datetime(1984, 9, 21)])
                
                # Get a canonicalized set of arguments.
                hashable = [(i, j) for i, j in kw.iteritems()]
                hashable.sort()
                hashable = tuple([self.asset.id, scope, latest] + list(args) + hashable)
                
                log.debug("Cache hashable: %r", hashable)
                
                def createfunc():
                    log.debug("Cache invalid or non-existant for %r, generating.", self.asset)
                    return fn(self, *args, **kw)
                
                result = viewcache.get_value(key=hashable, createfunc=createfunc, expiretime=cache)
                if isinstance(result, dict): result.update(cmf=cmf_namespace, asset=self.asset, controller=self)
                return result
            
            result = fn(self, *args, **kw)
            if isinstance(result, dict): result.update(cmf=cmf_namespace, asset=self.asset, controller=self)
            return result
        
        return wrapper
    
    return decorator


def action(cls, name, description=None, icon=None):
    """Mark a method as an action.
    
    Pass the decorator the short name (used for path construction), description, and a few optional values:
    
    `icon` -- An icon to represent this view in pretty lists.
    """
    
    # log.debug("%r action decorator initialized.  [%r, %r, icon=%r]", cls, name, description, icon)
    
    def decorator(fn):
        from cmf.components.asset.model import Asset
        
        def wrapper(self, *args, **kw):
            cmf_namespace = process(self)
            
            result = fn(self, *args, **kw)
            if isinstance(result, dict): result.update(cmf=cmf_namespace, asset=self.asset, controller=self)
            return result
        
        return wrapper
    
    return decorator