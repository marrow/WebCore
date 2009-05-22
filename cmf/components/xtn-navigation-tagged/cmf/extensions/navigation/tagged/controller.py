# encoding: utf-8

from cmf.components.extension.controller import Extension


__all__ = ['TaggedNavigationController']


class TaggedNavigationController(Extension):
    template = 'cmf.extensions.navigation.tagged.views.navigation'
    
    @property
    def namespace(self):
        """Return a database query for the navigation."""
        
        from cmf.components.asset.model import session, Asset, Tag
        
        query = Asset.query.filter(Asset._tags.any(Tag.name.startswith('navigation'))).order_by(Asset.l)
        
        # TODO: Cache the results, if possible.
        
        return dict(taggedNavigation=query)