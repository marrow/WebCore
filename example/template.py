# encoding: utf-8

"""Template rendering sample application.

This renders the test.html file contained in the current working directory.
"""


def template(context):
	context.log.info("Returning template result.")
	return 'mako:./template.html', dict()


if __name__ == '__main__':
	from web.core import Application
	from web.ext.template import TemplateExtension
	
	# Create the underlying WSGI application, passing the extensions to it.
	app = Application(template, extensions=[TemplateExtension()])
	
	# Start the development HTTP server.
	app.serve('wsgiref')

