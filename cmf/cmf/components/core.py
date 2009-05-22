# encoding: utf-8

"""

Base asset controller.

"""

from hashlib                import md5

from tg                     import request, session, expose, flash, redirect, url, TGController
from tg.decorators          import Decoration
from pylons.controllers.util import abort
from pylons.i18n            import ugettext as _

from cmf.api                import IAction, IView
from cmf.core               import components
from cmf.hooks              import hooks

from cmf.components.asset.model import Asset


log = __import__('logging').getLogger(__name__)
__all__ = ['BaseController']


class BaseController(TGController):
    """"""
    
    __repr__        = lambda self: '%s %s (%s %r)' % (self.__class__.__name__, self.asset.guid, self.asset.name, self.asset.title)
    
    
    def __init__(self, guid=None):
        """Initialize the controller for the given model instance."""
        
        super(BaseController, self).__init__()
        
        try:
            if isinstance(guid, Asset): self.asset = guid
            elif not guid: self.asset = Asset.query.filter_by(l=1).one()
            else: self.asset = Asset.get(guid)
            log.debug("Loaded asset %r for controller %r.", self.asset, self)
            
        except:
            log.exception("Error loading model instance for %r instance using %r.", self.__class__.__name__, guid)
            abort(404)
        
        if not isinstance(self, self.asset.Controller):
            log.exception("%r (%r) is not a %r instance.", self, self.__class__, self.asset.Controller)
            raise TypeError("%r (%r) is not a %r instance." % (self, self.__class__, self.asset.Controller))
        
        # Load up the actions and views for this asset.  TODO: Load them from available hooks, too, to allow extensions to extend/override base classes.
        
        def find_instances(cls):
            items = []
            
            for name in dir(self):
                value = getattr(self, name)
                #if callable(value) and name.startswith('_view_'):
                #    log.debug("Property called %r is callable: %r", name, value.__dict__)
                    
                if isinstance(value, cls): items.append((name, value))
            
            items.sort(key=lambda i: i[1]._counter, reverse=True)
            items = [i for i in items if i[1].authorized(self.asset)]
            
            return items
        
        self.actions = find_instances(IAction)
        self.views = find_instances(IView)
    
    @property
    def authorized(self):
        for func in hooks.authorized:
            if func(self.asset): return True
        
        return False
    
    @expose()
    def lookup(self, node, *remainder):
        log.debug("Looking in %r for %r *%r...", self, node, remainder)
        
        if node in ["", u"", "index", u"index"]:
            node = self.asset.default
            remainder = tuple([])
        
        if node.startswith('urn:uuid:'):
            record = Asset.get(node[9:])
            redirect(url([record.path] + list(remainder), **dict(request.params)))
        
        if ":" in node:
            if node.startswith('api:') and not session.get('cmf.authentication.account', False):
                session['cmf.authentication.target'] = request.path_info
                session['cmf.authentication.target.asset'] = record.guid
                session.save()
                
                flash("You do not have permission to access this resource.", "error")
                
                from cmf.components.authentication.model import Authentication
                redirect(Authentication.query.all()[0].path + '/action:authenticate')
            
            return self, ["_%s" % (node.replace(":", "_"), )] + list(remainder)
        
        if True:
            # TODO: Alternate lookup system using hashes.  Currently bypasses authorization checks.
            # Falls back on the standard recursive algorithm on failure.
            base = self.asset.path[1:]
            hashes = [md5(base+node).hexdigest()] + [md5('/'.join([base+node] + list(remainder[:i+1]))).hexdigest() for i in xrange(len(remainder))]
            fullpaths = [node] + ['/'.join([node] + list(remainder[:i+1])) for i in xrange(len(remainder))]
            paths = [node] + list(remainder)
            hashes.reverse()
            fullpaths.reverse()
            
            record = Asset.query.filter(Asset.pathhash.in_(hashes)).order_by('-l').first()
            if record:
                hashes.reverse()
                index = hashes.index(record.pathhash)
                instance = record.Controller(record) or abort(500)
                
                log.debug("Found %r at index %d based on hash with remainder: %r", record, index, paths[index+1:])
                
                return instance, paths[index+1:] if paths[index+1:] else [record.default]
            
            log.warn("Optimized path lookup by hash failed.")
        
        if isinstance(node, basestring):
            record = Asset.query.filter_by(name=node, parent=self.asset).first() or abort(404)
            instance = record.Controller(record) or abort(500)
            
            if not self.authorized:
                session['cmf.authentication.target'] = request.path_info
                session['cmf.authentication.target.asset'] = record.guid
                session.save()
                
                flash("You do not have permission to access this resource.", "error")
                
                from cmf.components.authentication.model import Authentication
                redirect(Authentication.query.all()[0].path + '/action:authenticate')

            return instance, remainder if remainder else [record.default]

        abort(404)