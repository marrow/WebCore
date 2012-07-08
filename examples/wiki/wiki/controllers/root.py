# encoding: utf-8

import textile

import web.core

from wiki import model as db


__all__ = ['RootController']
log = __import__('logging').getLogger(__name__)


class AJAXArticleForm(web.core.HTTPMethod):
    def __init__(self, name, article):
        self.name = name
        self.article = article
        super(AJAXArticleForm, self).__init__()

    def get(self):
        return 'wiki.templates.modify_form', dict(name=self.name, article=self.article)

    def post(self, name, content, **kw):
        if not self.article:
            self.article = db.Article()
            db.session.add(self.article)

        self.article.name = name
        self.article.content = content

        return textile.textile(self.article.content)


class ArticleForm(web.core.HTTPMethod):
    def __init__(self, name, article):
        self.name = name
        self.article = article
        super(ArticleForm, self).__init__()

    def get(self):
        return 'wiki.templates.modify', dict(name=self.name, article=self.article)

    def post(self, name, content, **kw):
        if not self.article:
            self.article = db.Article()
            db.session.add(self.article)

        self.article.name = name
        self.article.content = content

        url = web.core.url.compose('/', self.article.name)
        raise web.core.http.HTTPFound(location=url)


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
            url = web.core.url.compose('create')
            raise web.core.http.HTTPFound(url)

        content = textile.textile(self.article.content)

        return 'wiki.templates.view', dict(
                article=self.article,
                content=content
            )

    def delete(self):
        db.session.delete(self.article)
        raise web.core.http.HTTPFound(location=web.core.url('/'))


class RootController(web.core.Controller):
    def index(self):
        raise web.core.http.HTTPMovedPermanently(location=web.core.url("/WikiHome"))

    def Index(self):
        return 'wiki.templates.index', dict(
                articles=db.session.query(db.Article.name)
            )

    def __lookup__(self, article, *parts, **data):
        return ArticleController(unicode(article)), parts
