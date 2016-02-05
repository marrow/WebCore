# encoding: utf-8

"""A one-function WebCore 2 demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""


def basic(context, name="world"):
	return "Hello {name}.".format(name=name)


if __name__ == '__main__':
	from web.core.application import Application
	
	Application(basic).serve('waitress')
