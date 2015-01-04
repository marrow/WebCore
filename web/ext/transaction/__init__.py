# encoding: utf-8

try:
	import transaction
except ImportError:
	raise ImportError("Unable to import transaction; pip install transaction to fix this.")


class TransactionExtension(object):
	provides = ['transaction']

	def __init__(self):
		"""Executed to configure the extension."""
		
		self.transaction = transaction  # Helpful for debugging and testing.
		
		super(TransactionExtension, self).__init__()
	
	def start(self, context):
		"""Executed during application startup just after binding the server."""
		context.transaction = self.transaction
	
	def prepare(self, context):
		"""Executed during request set-up."""
		context.transaction.begin()
	
	def after(self, context, exc=None):
		"""Executed after dispatch has returned and the response populated, prior to anything being sent to the client."""
		
		transaction = context.transaction.transaction
		
		if exc or (hasattr(transaction, 'isDoomed') and transaction.isDoomed()):
			transaction.get().abort()
			return
		
		transaction.get().commit()
