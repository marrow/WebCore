# encoding: utf-8

# ## Imports

from __future__ import unicode_literals


# ## Module Globals

# Standard Logger object.
log = __import__('logging').getLogger(__name__)


# ## Extension

class TransactionExtension(object):
	"""Provide transaction support to WebCore extensions.
	
	The following extension callbacks participate in the transaction lifecycle, assuming an extension that `needs` or
	`uses` the `transaction` feature to ensure correct extension ordering:
	
	`start`: the underlying transaction machinery is configured at this point, allowing custom transactions to be run
		any time after application startup.
	
	`prepare`: if automatic behaviour is indicated, a per-request transaction will have been begun at this point.
	
	`begin` *new*: prepare a transaction
	
	This provides glue support and additional extension callbacks to support the following transaction lifecycle:
	
	1. All `prepare` callbacks are executed. If `autocommit` is truthy, a transaction is begun.
	2. All `begin` callbacks are executed.
	3. Some work happens.
	4. Eventually the `done` callbacks are executed.
	4. If `autocommit` is truthy, run all `vote` callbacks to determine if anything needs to be committed and it is safe to do so.
	5. If the vote passed, call all `commit` callbacks.
	6. If the vote failed, call all `abort` callbacks.
	"""
	
	provides = {'transaction'}  # Your own extension would specify this in its own `need` or `uses` attribute.
	signals = {'begin', '-vote', '-finish', '-abort'}  # Additional callbacks other extensions can use if enabled.
	
	def __init__(self, autocommit='success'):
		"""Configure WebCore transaction support.
		
		Determining when to autocommit is important; the value may be falsy, which implies never, literal True,
		implying always, or the string `success`, indicating to only commit when the response has a 2xx or 3xx status
		code.
		"""
		
		self.autocommit = autocommit
	
	def start(self, context):
		pass
	
	def prepare(self, context):  # Optional/conditional?
		pass
	
	def after(self, context):
		pass
	
	def __call__(self, context, app):
		pass
