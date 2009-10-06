# encoding: utf-8

import textile

import web

from web.extras.examples.wiki import model as db


__all__ = ['RootController']
log = __import__('logging').getLogger(__name__)



class AJAXArticleForm(web.core.RESTMethod):
    def __init__(self, name, article):
        self.name = name
        self.article = article
    
    def get(self):
        return 'web.extras.examples.wiki.templates.modify_form', dict(name=self.name, article=self.article)
    
    def post(self, name, content, **kw):
        if not self.article:
            self.article = db.Article()
            db.session.add(self.article)
        
        self.article.name = name
        self.article.content = content
        
        return textile.textile(self.article.content)


class ArticleForm(web.core.RESTMethod):
    def __init__(self, name, article):
        self.name = name
        self.article = article
    
    def get(self):
        return 'web.extras.examples.wiki.templates.modify', dict(name=self.name, article=self.article)
    
    def post(self, name, content, **kw):
        if not self.article:
            self.article = db.Article()
            db.session.add(self.article)
        
        self.article.name = name
        self.article.content = content
        
        raise web.core.http.HTTPFound(location='/' + self.article.name)


class ArticleController(web.core.Controller):
    def __init__(self, name):
        super(ArticleController, self).__init__()
        
        self.name = name
        self.article = db.Article.get(name)
        
        self.modify = ArticleForm(self.name, self.article)
        self.create = self.modify
        
        self.modify_ajax = AJAXArticleForm(self.name, self.article)
        self.create_ajax = self.modify_ajax
    
    def index(self):
        if not self.article:
            raise web.core.http.HTTPFound(location='/' + self.name + '/create')
        
        content = textile.textile(self.article.content)
        
        return 'web.extras.examples.wiki.templates.view', dict(
                article = self.article,
                content = content
            )
    
    def delete(self):
        db.session.delete(self.article)
        raise web.core.http.HTTPFound(location='/')


class RootController(web.core.Controller):
    def index(self):
        raise web.core.http.HTTPMovedPermanently(location="/WikiHome")
    
    def Index(self):
        return 'web.extras.examples.wiki.templates.index', dict(
                articles = db.session.query(db.Article.name)
            )
    
    def lookup(self, article, *parts, **data):
        return ArticleController(unicode(article)), parts
