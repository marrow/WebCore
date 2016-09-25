# encoding: utf-8

"""A one-function WebCore 2 demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""


def basic(context, name="world"):
	1/0
	return "Hello {name}.".format(name=name)


if __name__ == '__main__':
	from web.core import Application
	from web.ext.debug import DebugExtension
	
	Application(basic, extensions=[DebugExtension()]).serve('waitress')

