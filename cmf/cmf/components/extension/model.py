# encoding: utf-8

from elixir                 import using_options, Field, String, UnicodeText

import cmf.components.asset.model                           as model
# import cmf.components.extension.controller                  as controller


log = __import__('logging').getLogger(__name__)
__all__ = ['Extension']
__model__ = ['Extension']


class Extension(model.Asset):
    """Define the data model structures for extensions.
    
    No model is defined, a table is created to assist in easy querying.
    Subclasses should not use multi-table inheritance; instead, they should
    use 'single' inheritance to avoid creating wasteful single-row tables.
    
    Subclasses -do- still need to create their own model, even if it is only
    two lines.  This is to allow the ORM to correctly identify subclass
    instances, and for the framework to load the appropriate controller.
    
    For data structures, Extension subclasses should utilize anonymous
    inheritable properties.  Properties can be set on the instance, or
    on the root node.  Additionally, in the extension hooks, properties
    can be read from the node being accessed, allowing options to be
    overridden by the user for specific areas of the site."""
    
    # Controller = controller.ExtensionController
    using_options(tablename='extensions', inheritance='multi', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.components.extension.controller import ExtensionController
        return ExtensionController
