# encoding: utf-8

from tw.mods.base import HostFramework


__all__ = ['WebCoreHostFramework']


class WebCoreHostFramework(HostFramework):
    def url(self, url):
        # TODO: Update to use web.core.url
        return ''.join([self.request_local.environ['toscawidgets.prefix'], url])
