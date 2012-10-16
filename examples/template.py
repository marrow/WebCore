# encoding: utf-8

"""Template rendering sample application.

This renders the test.html file contained in the current working directory.
"""


def template(context):
    context.log.warning("Returning template result.")
    return 'mako:./template.html', dict()


if __name__ == '__main__':
    from marrow.server.http import HTTPServer
    
    from web.core.application import Application
    from web.ext.template import TemplateExtension
    
    HTTPServer('127.0.0.1', 8080, application=Application(template, dict(extensions=dict(
            template = TemplateExtension()
        )))).start()
