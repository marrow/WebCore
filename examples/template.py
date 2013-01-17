# encoding: utf-8

"""Template rendering sample application.

This renders the test.html file contained in the current working directory.
"""


def template(context):
    context.log.info("Returning template result.")
    return 'mako:./template.html', dict()


if __name__ == '__main__':
    from marrow.server.http import HTTPServer
    
    from web.core.application import Application
    from web.ext.template import TemplateExtension
    
    # Configure the extensions needed for this example:
    config = dict(
            extensions = [
                    TemplateExtension()
                ])

    # Create the underlying WSGI application, passing the extensions to it.
    app = Application(template, **config)

    # Start the development HTTP server.
    HTTPServer('127.0.0.1', 8080, application=app).start()
