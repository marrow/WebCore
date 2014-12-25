# encoding: utf-8

"""A one-function WebCore 2 demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""


def basic(context):
	#context.log.info("Returning plain text content.")
	#context.response.mime = b'text/plain'
	return "Hello world."


if __name__ == '__main__':
	from web.core.application import Application
	import logging
	
	logging.basicConfig(level=logging.WARN)
	
	Application(basic).serve('wsgiref')
