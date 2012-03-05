# encoding: utf-8

"""Basic route-based demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""

from web.dialect.route import route


class Root(object):
    __dispatch__ = 'route'
    
    @route('/')
    def index(self):
        return "Root handler."
    
    @route('/page/{name}')
    def page(self, name):
        return "Page handler for: " + name


if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer

    HTTPServer('127.0.0.1', 8080, application=Application(Root)).start()
