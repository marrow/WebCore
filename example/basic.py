# encoding: utf-8

"""A one-function WebCore 2 demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""


def basic(context):
	return "Hello world."


if __name__ == '__main__':
	from web.core.application import Application
	
	Application(basic).serve('waitress')
