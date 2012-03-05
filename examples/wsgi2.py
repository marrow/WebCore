# encoding: utf-8

"""Enhanced WSGI 2 (PEP 444) test application.

The "enhanced" part is getting a copy of the context rather than request environ.
"""


def enhanced(context):
    return b'200 OK', [(b'Content-Type', b'text/plain'), (b'Content-Length', b'12')], [b'Hello world.']


if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer
    
    HTTPServer('127.0.0.1', 8080, application=Application(enhanced)).start()
