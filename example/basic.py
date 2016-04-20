# encoding: utf-8

"""A one-function WebCore 2 demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""


def basic(context, name="world"):
	"""Say hello.
	
	This can be tested easily using cURL from the command line:
	
		curl http://localhost:8080/  # Default value via GET.
		curl http://localhost:8080/Alice  # Positionally specified via GET.
		curl -d name=Eve http://localhost:8080/  # Form-encoded value via POST.
	"""
	return "Hello {name}.".format(name=name)


if __name__ == '__main__':
	from web.core import Application
	
	Application(basic).serve('waitress')

