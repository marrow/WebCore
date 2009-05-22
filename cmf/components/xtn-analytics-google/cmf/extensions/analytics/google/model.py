# encoding: utf-8

from elixir                 import using_options # , Field, String, UnicodeText, Boolean

from cmf.components.extension.model import Extension


__all__ = ['GoogleAnalytics']
__model__ = ['GoogleAnalytics']


class GoogleAnalytics(Extension):
    icon = 'base-extension'
    using_options(inheritance='single', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.extensions.analytics.google.controller import GoogleAnalyticsController
        return GoogleAnalyticsController
