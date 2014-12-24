# encoding: utf-8

"""Exception handling test application.

This application always raises 404 Not Found.
"""

from marrow.wsgi.exceptions import HTTPNotFound


def exception(context):
    raise HTTPNotFound()


if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer
    
    HTTPServer('127.0.0.1', 8080, application=Application(exception)).start()
