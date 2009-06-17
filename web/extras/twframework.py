from tw.mods.base import HostFramework

class YAPWFHostFramework(HostFramework):
    def url(self, url):
        return ''.join([self.request_local.environ['toscawidgets.prefix'], url])