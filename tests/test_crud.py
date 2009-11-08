# encoding: utf-8

from unittest import TestCase

from webob import Request

import web
from web.core import Application, Controller

from common import PlainController, WebTestCase


class ObjectController(PlainController):
    def __init__(self, last, first):
        self.last, self.first = last, first
    
    def index(self):
        return "viewing %s %s" % (self.first, self.last)
    
    def modify(self):
        return "modifying %s %s" % (self.first, self.last)
    
    def delete(self):
        return "deleting %s %s" % (self.first, self.last)


class DefController(PlainController):
    def default(self, *args, **kw):
        return "default controller for %s" % (" ".join(args), )


class RootController(PlainController):
    catchall = DefController()
    
    def index(self):
        return "listing records"
    
    def create(self):
        return "creating a record"
    
    def lookup(self, last, first, *parts, **data):
        return ObjectController(last, first), parts


test_config = {'debug': True, 'web.widgets': False, 'web.sessions': False, 'web.compress': False, 'web.static': False}


class CRUDDispatch(WebTestCase):
    app = Application.factory(root=RootController, **test_config)
    
    def test_basic(self):
        self.assertResponse('/', body="listing records")
        self.assertResponse('/create', body="creating a record")
    
    def test_object(self):
        self.assertResponse('/Dole/Bob/', body="viewing Bob Dole")
        self.assertResponse('/Dole/Bob/modify', body="modifying Bob Dole")
        self.assertResponse('/Dole/Bob/delete', body="deleting Bob Dole")
    
    def test_default(self):
        self.assertResponse('/catchall/foo/bar', body="default controller for foo bar")
        self.assertResponse('/catchall/_private', body="default controller for _private")
