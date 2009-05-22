# encoding: utf-8

"""Base asset model.

All asset types must descend from this class."""

import                      logging
import                      re

from hashlib                import md5
from uuid                   import uuid4
                                        
from elixir                 import session
from elixir                 import Entity, Field
from elixir                 import String, Unicode, Boolean, PickleType, DateTime, Integer, UnicodeText
from elixir                 import ManyToMany, ManyToOne, OneToMany
from elixir                 import using_options, using_table_options
from sqlalchemy             import UniqueConstraint
from sqlalchemy.sql         import func, and_, or_

from sqlalchemy.ext.associationproxy    import association_proxy
from sqlalchemy.orm.collections         import attribute_mapped_collection


TAGGER = re.compile(r'("[^"]*"|[^ ]*)(?: *|$)')
log = logging.getLogger(__name__)
__all__ = ['Tag', 'Property', 'Asset']
__model__ = ['Tag', 'Property', 'Asset']


class Tag(Entity):
    """TODO:Docstring incomplete."""
    
    __repr__        = lambda self: 'Tag %r' % (self.name, )
    __str__         = lambda self: str(self.name)
    using_options(tablename='tags', order_by='name')
    
    name            = Field(Unicode(200), primary_key=True)
    assets          = ManyToMany('Asset')
    
    @classmethod
    def create(cls, name):
        tag = cls.get(unicode(name))
        if tag: return tag
        
        return cls(name=unicode(name))
    
    @classmethod
    def split(cls, value):
        if not isinstance(value, basestring): raise TypeError("Invalid type for argument 'value'.")
        if not value or not value.strip(): return []
        
        tags = []
        potential_tags = TAGGER.split(value.strip())
        for tag in potential_tags:
            if tag.strip(' "'): tags.append(tag.strip(' "'))
        
        return tags
    
    @classmethod
    def join(cls, value):
        if not isinstance(value, (tuple, list)): raise TypeError("Invalid type for argument 'value'.")
        if not value: return ""
        
        tags = []
        for tag in value:
            if ' ' in tag: tags.append('"%s"' % (tag, ))
            else: tags.append(tag)
        return " ".join(tags)


class Property(Entity):
    """TODO:Docstring incomplete."""
    
    __repr__        = lambda self: 'Property %r = %r' % (self.name, self.value)
    __str__         = lambda self: self.name
    using_options(tablename='properties', order_by=['asset_guid', 'name'])
    
    asset           = ManyToOne('Asset')
    name            = Field(String(250))
    value           = Field(PickleType, default=None)
    inheritable     = Field(Boolean, default=False)
    
    created         = Field(DateTime, default=func.now())
    updated         = Field(DateTime)
    
    @classmethod
    def create(cls, name, value):
        return cls(name=name, value=value)


class ProperyInheritance(object):
    """A dictionary (associative array) that retreives the Property for a given asset.
    
    This differs from the _properties association proxy in that it will inherit properties from parent assets."""
    
    def __init__(self, asset):
        """We'll need to know the asset we are returning properties for later."""
        
        self.asset = asset
    
    def __repr__(self):
        """Return a string representation of a PropertyInheritance instance."""
        
        return "PropertyInheritance(%r)" % (self.asset)
    
    def __setitem__(self, key, value):
        """Create or update a property on the given asset. Overrides inherited properties.
        
        Properties set this way will not be inheritable."""
        
        self.asset._properties[key] = value
    
    def get(self, name, fallback=None, inherited=True, value=False):
        """Look up and return the given property.
        
        If inherited is False, only get the property directly from the asset.
        If value is True, don't return the Property and Asset instances, return the property's value.
        
        Returns the property and asset defining the property."""
        
        if not inherited:
            if value: return self.asset._properties[name]
            return (Property.query.filter_by(asset=self.asset).one(), self.asset)
        
        try:
            prop, asset = session.query(Property, Asset) \
                .filter(or_(Property.inheritable == 1, Property.asset == self.asset)) \
                .filter(Property.name == name) \
                .filter(Property.asset_guid == Asset.guid) \
                .filter(and_(Asset.l <= self.asset.l, Asset.r >= self.asset.r)) \
                .first()
            
            if prop and value: return prop.value
            return prop, asset
        
        except:
            log.exception("Error looking up property.")
            pass
        
        return fallback if value else (fallback, None)
    
    def __getitem__(self, name):
        """Lookup inherited properties using `properties['foo.bar.baz']` syntax.
        
        This can only return a single value, so we return the property value, not the property."""
        
        return self.get(name, value=True)
    
    def __delitem__(self, name):
        """Delete the given property."""
        
        prop = self.get(name, inherited=False)
        session.delete(prop)
        session.commit()


class Asset(Entity):
    """TODO:Docstring incomplete."""
    
    __repr__        = lambda self: '%s %s (%s %r)' % (self.__class__.__name__, self.guid, self.name, self.title)
    __str__         = lambda self: self.name
    using_options(tablename='assets', inheritance='multi', polymorphic='kind', order_by='l')
    using_table_options(UniqueConstraint('parent_guid', 'name'))
    
    @property
    def Controller(self):
        from cmf.components.asset.controller import AssetController
        return AssetController
    
    _controller     = None
    
    @property
    def controller(self):
        if not self._controller: self._controller = self.Controller(self)
        return self._controller
    
    id              = property(lambda self: self.guid)
    guid            = Field(String(36), default=lambda: str(uuid4()), primary_key=True)
    
    l, r            = Field(Integer, default=0), Field(Integer, default=0)
    parent          = ManyToOne('Asset')
    children        = OneToMany('Asset', inverse='parent', cascade='all', lazy='dynamic')
    
    pathhash        = Field(String(48))
    
    name            = Field(String(250), required=True)
    title           = Field(Unicode(250))
    description     = Field(UnicodeText)
    
    default         = Field(String(250), default="view:default")
    
    _tags           = ManyToMany('Tag')
    tags            = association_proxy('_tags', 'name', creator=Tag.create)
    
    _property       = OneToMany('Property', cascade='all,delete-orphan', collection_class=attribute_mapped_collection('name'))
    _properties     = association_proxy('_property', 'value', creator=Property.create)
    
    _inheritable    = None
    
    def _get_inheritable(self):
        if not self._inheritable:
            self._inheritable = ProperyInheritance(self)
        
        return self._inheritable
    
    properties      = property(_get_inheritable)
    
    ancestors       = property(lambda self: Asset.query.filter(Asset.r > self.r).filter(Asset.l < self.l), doc="Return all ancestors of this asset.")
    descendants     = property(lambda self: Asset.query.filter(Asset.r < self.r).filter(Asset.l > self.l), doc="Return all descendants of this asset.")
    depth           = property(lambda self: self.ancestors.count() + 1, doc="Return the current asset's depth in the tree.")
    siblings        = property(lambda self: (self.parent.children.filter(Asset.r < self.r), self.parent.children.filter(Asset.l > self.l)), doc="Return two lists; the first are siblings to the left, the second, to the right.")
    
    permalink       = property(lambda self: "/urn:uuid:%s" % self.guid, doc="Return a 'permalink' URL for this asset.")
    path            = property(lambda self: "" if not self.parent else "/" + "/".join([i.name for i in self.ancestors.all()[1:]] + [self.name]), doc="Return the full path to this asset.")
    
    owner           = ManyToOne('Asset')
    created         = Field(DateTime, default=func.now())
    modified        = Field(DateTime)
    published       = Field(DateTime)
    retracted       = Field(DateTime)
    
    icon            = property(lambda self: "base-" + self.__class__.__name__.lower())
    
    
    @classmethod
    def stargate(cls, left=None, right=None, value=2, both=None):
        """Open a hole in the left/right structure.  Alternatively, with a negative value, close a hole."""
        
        if both:
            Asset.table.update(both, values=dict(l = Asset.l + value, r = Asset.r + value)).execute()
        
        if left:
            Asset.table.update(left, values=dict(l = Asset.l + value)).execute()
        
        if right:
            Asset.table.update(right, values=dict(r = Asset.r + value)).execute()
        
        session.commit()
        
        # Expire the cache of the l and r columns for every Asset.
        log.info("Expiring l and r columns...")
        [session.expire(obj, ['l', 'r']) for obj in session if isinstance(obj, Asset)]
    
    
    def attach(self, node, after=True, below=True):
        """Attach an object as a child or sibling of the current object."""
        
        session.commit()
        
        log.debug("Attaching %r to %r (%s and %s)", node, self, "after" if after else "before", "below" if below else "level with")
        
        if self is node:
            raise Exception, "You can not attach a node to itself."
        
        if node in self.ancestors.all():
            raise Exception, "Infinite loops give coders headaches.  Putting %r inside %r is a bad idea." % (node, self)
        
        if node.l and node.r:
            # Run some additional integrity checks before modifying the database.
            assert node.l < node.r, "This object can not be moved as its positional relationship information is corrupt."
            assert node.descendants.count() == ( node.r - node.l - 1 ) / 2, "This node is missing descendants and can not be moved."
        
        count = ( 1 + node.descendants.count() ) * 2
        log.debug("l=%r, r=%r, c=%r", node.l, node.r, count)
        
        try:
            if below:
                if after: log.debug("self.stargate(Asset.l >= self.r, Asset.r >= self.r, count)")
                else: log.debug("self.stargate(Asset.l > self.l, Asset.r > self.l, count)")
                
                if after: self.stargate(Asset.l >= self.r, Asset.r >= self.r, count)
                else: self.stargate(Asset.l > self.l, Asset.r > self.l, count)
            else:
                if after: log.debug("self.stargate(Asset.l > self.r, Asset.r > self.r, count)")
                else: log.debug("self.stargate(Asset.l >= self.l, Asset.r >= self.l, count)")
                
                if after: self.stargate(Asset.l > self.r, Asset.r > self.r, count)
                else: self.stargate(Asset.l >= self.l, Asset.r >= self.l, count)
            
            if not node.l or not node.r:
                # This node is currently unassigned and/or corrupt.
                if below:
                    if after: node.l, node.r = self.r - 2, self.r - 1
                    else: node.l, node.r = self.l + 1, self.l + 2
                    node.parent = self
                
                else:
                    if after: node.l, node.r = self.r + 1, self.r + 2
                    else: node.l, node.r = self.l - 2, self.l - 1
                    node.parent = self.parent
                
                node.pathhash = md5(node.path[1:]).hexdigest()
                session.commit()
                return

            # This node was already placed in the tree and needs to be moved.  How far?
            if below:
                if after: delta = self.r - node.r - 1
                else: delta = self.l - node.l + 1
            else:
                if after: delta = self.r - node.r + 2
                else: delta = self.l - node.l - 2
            
            log.debug("delta=%d", delta)

            # Migrate the node and its ancestors to its new location.
            hole = node.l
            self.stargate(value=delta, both=and_(Asset.l >= node.l, Asset.r <= node.r))

            # Close the resulting hole.
            self.stargate(Asset.l >= hole, Asset.r >= hole, -count)
            
            if below: node.parent = self
            node.pathhash = md5(node.path[1:]).hexdigest()

        except:
            session.rollback()
            log.exception("Exception raised while attaching %r to %r.  [after=%r, below=%r]", node, self, after, below)
            raise

        else:
            session.commit()
