# encoding: utf-8

class Root:
	def __init__(self, context):
		self._ctx = context
	
	def test(self, *args):
		assert not args

if __name__ == '__main__':
	__import__('scaffold').serve(Root)
	# GET /test - Should not drop into debugger. (Args should be empty.)
