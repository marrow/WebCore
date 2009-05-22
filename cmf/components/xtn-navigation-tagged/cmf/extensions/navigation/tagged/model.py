# encoding: utf-8

from elixir                 import using_options # , Field, String, UnicodeText, Boolean

from cmf.components.extension.model import Extension


__all__ = ['TaggedNavigation']
__model__ = ['TaggedNavigation']


class TaggedNavigation(Extension):
    icon = 'base-extension'
    using_options(inheritance='single', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.extensions.navigation.tagged.controller import TaggedNavigationController
        return TaggedNavigationController
