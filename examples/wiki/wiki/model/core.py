# encoding: utf-8

from sqlalchemy import *
from sqlalchemy.orm import *

from wiki.model.base import Base


__all__ = ['Article']


class Article(Base):
    __tablename__ = 'articles'

    name = Column(Unicode(250), primary_key=True)
    content = Column(UnicodeText)
