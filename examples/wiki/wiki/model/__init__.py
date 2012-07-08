# encoding: utf-8

from paste.registry import StackedObjectProxy

from wiki.model.base import *
from wiki.model.core import *


metadata = Base.metadata
session = StackedObjectProxy()


def ready(session):
    metadata.create_all()
    
    if not session.query(Article).count():
        session.add(Article(name="WikiHome", content="h1. Define your content."))
