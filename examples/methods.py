# encoding: utf-8

"""Slightly more advanced example application."""

from web.dialect.helper import method


class Root(object):
    @method.get
    def login(self):
        return "Present login form."
    
    @login.post
    def login(self, **data):
        # can call login.get() to explicitly call that handler.
        return "Actually log in."



if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer

    HTTPServer('127.0.0.1', 8080, application=Application(Root)).start()
