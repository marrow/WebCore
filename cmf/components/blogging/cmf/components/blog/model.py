# encoding: utf-8

from datetime               import timedelta

from elixir                 import Entity, Field
from elixir                 import String, Unicode, Boolean, PickleType, DateTime, Integer, UnicodeText, Interval
from elixir                 import ManyToMany, ManyToOne, OneToMany
from elixir                 import using_options, using_table_options

from cmf.components.folder.model import Folder


log = __import__('logging').getLogger(__name__)
__all__ = ['Blog']
__model__ = ['Blog']


class Blog(Folder):
    """TODO:Docstring incomplete."""
    
    using_options(tablename='blogs', inheritance='multi', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.components.blog.controller import BlogController
        return BlogController
    
    fresh           = Field(Interval, default=timedelta(days=7))        # Within what range should assets be marked as "new"?
    refresh         = Field(Boolean, default=True)                      # Should updated entries be treated as "new"?
    
    show            = Field(Integer, default=15)                        # Number of days/posts to show.
    days            = Field(Boolean, default=False)                     # False: show last n posts; True: show last n days
