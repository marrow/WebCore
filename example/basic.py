"""A one-function WebCore 2 demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""


def basic(context, name:str="world") -> str:
	"""Say hello.
	
	This can be tested easily using cURL from the command line:
	
		curl http://localhost:8080/  # Default value via GET.
		curl http://localhost:8080/Alice  # Positionally specified via GET.
		curl -d name=Eve http://localhost:8080/  # Form-encoded value via POST.
	
	To demonstrate the utility extensions used here, try out the following and watch the server logs:
	
		curl 'http://localhost:8080/?bob=dole'
		curl 'http://localhost:8080/?utm_source=web'
		curl 'http://localhost:8080/Bob?name=Dole&utm_source=web'
	
	Try those again after re-launching the web server via:
	
		python3 -X dev example/basic.py
	"""
	
	return "Hello {name}.".format(name=name)


if __name__ == '__main__':
	from web.core import Application
	
	Application(basic, extensions=[
			'kwargs.elision',
		], logging={'level': 'debug'}).serve('waitress', threads=16)
