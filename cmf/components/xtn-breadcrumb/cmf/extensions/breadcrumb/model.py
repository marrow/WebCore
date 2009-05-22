# encoding: utf-8

from elixir                 import using_options # , Field, String, UnicodeText, Boolean

from cmf.components.extension.model import Extension


__all__ = ['Breadcrumb']
__model__ = ['Breadcrumb']


class Breadcrumb(Extension):
    icon = 'base-extension'
    using_options(inheritance='single', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.extensions.breadcrumb.controller import BreadcrumbController
        return BreadcrumbController
