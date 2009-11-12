# encoding: utf-8

from tw.mods.base import HostFramework



class WebCoreHostFramework(HostFramework):
    def url(self, url):
        return ''.join([self.request_local.environ['toscawidgets.prefix'], url])
