# encoding: utf-8

from cmf.components.extension.controller import Extension


__all__ = ['BreadcrumbController']


class BreadcrumbController(Extension):
    template = 'cmf.extensions.breadcrumb.views.breadcrumb'