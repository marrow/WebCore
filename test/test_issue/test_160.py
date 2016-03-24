# encoding: utf-8

class Root:
	def __init__(self, context):
		self._ctx = context

if __name__ == '__main__':
	__import__('scaffold').serve(Root)
	# GET /test - Should 404.
