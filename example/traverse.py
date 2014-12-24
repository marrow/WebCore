# encoding: utf-8

"""Basic traversal demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""


class Root(object):
    __dispatch__ = 'traversal'

    def __getitem__(self, name):
        return dict(about="About us.", contact="Contact information.")


if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer

    HTTPServer('127.0.0.1', 8080, application=Application(Root)).start()
