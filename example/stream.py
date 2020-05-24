from random import randint
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError


def mul(x, y):
	sleep(0.125)
	return ('text/plain', "{0} * {1} = {2}\n".format(x, y, x * y))


executor = ThreadPoolExecutor(10)


def root(context):
	"""Multipart AJAX request example.
	
	See: http://test.getify.com/mpAjax/description.html
	"""
	
	response = context.response
	
	parts = []
	
	for i in range(12):
		for j in range(12):
			parts.append(executor.submit(mul, i, j))
	
	def stream(parts, timeout=None):
		try:
			for future in as_completed(parts, timeout):
				mime, result = future.result()
				result = result.encode('utf8')
				
				yield "!!!!!!=_NextPart_{num}\nContent-Type: {mime}\nContent-Length: {length}\n\n".format(
						num = randint(100000000, 999999999),
						mime = mime,
						length = len(result)
					).encode('utf8') + result
		
		except TimeoutError:
			for future in parts:
				future.cancel()
	
	response.content_length = None
	response.app_iter = stream(parts, 0.2)
	
	return response


if __name__ == '__main__':
	from web.core import Application
	
	# wsgiref streams the chunks correctly, waitress buffers in 18000 byte chunks.
	Application(root, logging={'level': 'debug'}).serve('waitress', send_bytes=1)
