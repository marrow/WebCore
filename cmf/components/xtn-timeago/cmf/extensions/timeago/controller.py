# encoding: utf-8

from cmf.components.extension.controller import Extension

from tw.timeago import timeago_js


__all__ = ['TimeAgoController']


class TimeAgoController(Extension):
    def inject(self, controller):
        timeago_js.inject()