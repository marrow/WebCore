"""Exception handling test application.

This application always raises 404 Not Found.
"""

from webob.exc import HTTPNotFound


def exception(context):
	raise HTTPNotFound()


if __name__ == '__main__':
	from web.core import Application
	Application(exception).serve('wsgiref')
