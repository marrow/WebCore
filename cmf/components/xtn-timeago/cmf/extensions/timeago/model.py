# encoding: utf-8

from elixir                 import using_options # , Field, String, UnicodeText, Boolean

from cmf.components.extension.model import Extension


__all__ = ['TimeAgo']
__model__ = ['TimeAgo']


class TimeAgo(Extension):
    icon = 'base-extension'
    using_options(inheritance='single', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.extensions.timeago.controller import TimeAgoController
        return TimeAgoController
