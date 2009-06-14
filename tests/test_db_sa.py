# encoding: utf-8

from unittest import TestCase

from webob import Request

import web
from web.core import Application, Controller

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata



class RootController(Controller):
    def __before__(self, *parts, **data):
        web.core.response.content_type = "text/plain"
        return super(RootController, self).__before__(*parts, **data)
    
    def index(self):
        return "success"
    
    def arg(self, foo):
        return "got %s" % (foo, )
    
    def unicode(self):
        return u"Unicode text."


class SASessions(TestCase):
    app = Application.factory(root=RootController, debug=False, **{'db.engine': 'sqlalchemy', 'db.model': locals(), 'db.sqlalchemy.url': 'sqlite:///:memory:'})
    
    def test_index(self):
        response = Request.blank('/').get_response(self.app)
        
        assert response.status == "200 OK"
        assert response.content_type == "text/plain"
        assert response.body == "success"
