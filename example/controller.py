# encoding: utf-8

"""Basic class-based demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""

from web.app.static import static


class Root(object):
	def __init__(self, context):
		self._ctx = context
	
	def __call__(self):
		"""Handle "index" lookups."""
		return "Path: /"
	
	def index(self):
		"""Handle calls to /index -- this is no longer the 'default' index lookup."""
		return "Path: /index"
	
	foo = "Static string!"
	bar = "mako:./template.html", dict()
	
	config = open('controller.yaml', 'rb')
	
	static = static('./', dict(html='mako'))


if __name__ == '__main__':
	from web.core.application import Application
	from web.ext.template import TemplateExtension
	from web.ext.analytic import AnalyticsExtension
	
	Application(Root, logging={'level': 'debug'}, extensions=[AnalyticsExtension(), TemplateExtension()]).serve('waitress')
