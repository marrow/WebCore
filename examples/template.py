# encoding: utf-8

"""Template rendering sample application.

This renders the test.html file contained in the current working directory.
"""


def template(context):
    context.log.warning("Returning template result.")
    return 'mako:./examples/template.html', dict()


if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer
    
    HTTPServer('127.0.0.1', 8080, application=Application(template)).start()
