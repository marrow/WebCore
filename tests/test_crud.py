# encoding: utf-8

from unittest import TestCase

from webob import Request

import web
from web.core import Application, Controller

from common import PlainController


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
    
    


class CRUDDispatch(TestCase):
    app = Application.factory(root=RootController, buffet=False, widgets=False, beaker=False, debug=False)
    
    def test_basic(self):
        response = Request.blank('/').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "listing records"
        
        response = Request.blank('/create').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "creating a record"
    
    def test_object(self):
        response = Request.blank('/Dole/Bob/').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "viewing Bob Dole"
        
        response = Request.blank('/Dole/Bob/modify').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "modifying Bob Dole"
        
        response = Request.blank('/Dole/Bob/delete').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "deleting Bob Dole"
    
    def test_default(self):
        response = Request.blank('/catchall/foo/bar').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "default controller for foo bar"
    