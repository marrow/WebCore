# encoding: utf-8

from paste.registry import StackedObjectProxy

from wiki.model.base import *
from wiki.model.core import *


metadata = Base.metadata
session = StackedObjectProxy()



def prepare():
    metadata.create_all()

def populate(session, table):
    if table == 'articles':
        session.add(Article(name="WikiHome", content="h1. Define your content."))
