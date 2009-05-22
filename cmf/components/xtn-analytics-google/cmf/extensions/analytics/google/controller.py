# encoding: utf-8

from cmf.components.extension.controller import Extension

from tw.api                 import Widget, JSLink, JSSource


__all__ = ['GoogleAnalyticsController']


class GoogleAnalyticsLink(JSLink):
    def _get_link(self):
        # TODO: Determine if we are being accessed via HTTPS.
        return 'http://www.google-analytics.com/ga.js'
        return 'https://ssl.google-analytics.com/ga.js'
    
    def _set_link(self, value):
        pass
    
    link = property(_get_link, _set_link)


analytics_js                = GoogleAnalyticsLink()


class GoogleAnalytics(JSSource):
    location = 'bodybottom'
    src = """try { var pageTracker = _gat._getTracker("$account"); pageTracker._initData(); pageTracker._trackPageview(); } catch (err) {}"""
    source_vars = ['account']
    account = ''
    javascript = [analytics_js]


class GoogleAnalyticsController(Extension):
    """TODO: Docstring incomplete."""
    
    def inject(self, controller):
        GoogleAnalytics(account=controller.asset.properties['cmf.analytics.google:account']).inject()
