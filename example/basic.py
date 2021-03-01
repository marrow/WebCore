"""A one-function WebCore 2 demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""

import logging

from web.core.typing import Context, Optional


def greet(context:Optional[Context]=None, name:str="world") -> str:
	"""Say hello.
	
	The context is optional (possible to omit or None may be passed in) because in this example it is unused. This has
	the side-effect of making this function a simple, usable Python function, usable outside the context of a web
	interface. However, spinning this up for testing as a web service can be easily accomplished by executing:
	
		python example/basic.py
	
	Then utilize cURL from the command prompt:
	
		curl -v http://localhost:8080/  # Default value via GET.
		curl -v http://localhost:8080/Alice  # Positionally specified via GET.
		curl -v -d name=Eve http://localhost:8080/  # Form-encoded value via POST.
	
	To demonstrate the utility extension used here, try out the following and watch the server logs:
	
		curl -v 'http://localhost:8080/?bob=dole'
		curl -v 'http://localhost:8080/?utm_source=web'
		curl -v 'http://localhost:8080/Bob?name=Dole&utm_source=web'
		curl -v 'http://localhost:8080/Bob/Dole'
	
	Try those again after re-launching the web server via:
	
		python3 -X dev example/basic.py
	"""
	
	logging.debug("This is a diagnostic situation.")
	logging.info("This is an informational situation.", extra=dict(foo="bar", baz=27))
	logging.warning("This is a warning situation.")
	logging.error("This is an error situation.")
	logging.critical("This is a critical situation.")
	
	return f"Hello {name}."


if __name__ == '__main__':
	from web.core import Application
	
	Application(greet, extensions=['kwargs.elision'], logging={'level': 'debug' if __debug__ else 'info'}) \
			.serve('waitress', listen='127.0.0.1:8080 [::1]:8080', threads=4)
