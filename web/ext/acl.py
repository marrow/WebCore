# encoding: utf-8

"""Access Control List predicate-based security.

A predicate, to WebCore, is any callable object that receives the context as its first positional argument and returns
a boolean, or None. Two methods of making them configurable: functools.partial assignment of keyword arguments, or use
of classes (configurable via construction) with a __call__ method, accepting the context. Returning True authorizes
the action the predicate is being used with. False explicitly denies the action the predicate is being used with. None
means this predicate does not care as to the outcome of authorization, for whatever reason. The default policy if no
predicates match is to deny, in most instances.
"""

# ## Imports

from __future__ import unicode_literals

from webob.exc import HTTPNotAuthorized

from web.core.util import safe_name


# ## Module Globals

log = __import__('logging').getLogger(__name__)


# ## Extension

class ACLExtension(object):
	"""Access control list extension.
	
	Predicates are gathered as dispatch descends through objects, collecting them from the `__acl__` attribute.
	If any object defines `__acl_inherit__` as a falsy value the ACL gathered so far is cleared before continuing.
	"""
	
	provides = {'acl'}
	
	def __init__(self, base=None):
		"""Configure the ACL extension by defining an optional base policy.
		
		This policy will be used as the base for every request; these are evaluated first, always.
		"""
		self.base_policy = [(None, i, self) for i in base] if base else []
	
	# ### Request-Level Callbacks
	
	def prepare(self, context):
		"""Add the usual suspects to the context.
		
		This adds `acl` to the per-request context.
		"""
		
		if __debug__:
			log.debug("Preparing request context with ACL.", extra=dict(request=id(context)))
		
		context.acl = list(self.base_policy)
	
	def dispatch(self, context, consumed, handler, is_endpoint):
		"""Called as dispatch descends into a tier.
		
		The ACL extension uses this to build up the current request's ACL.
		"""
		
		acl = getattr(handler, '__acl__', [])
		inherit = getattr(handler, '__acl_inherit__', True)
		
		if __debug__:
			log.debug("Handling dispatch event.", extra=dict(
					request = id(context),
					consumed = consumed,
					handler = safe_name(handler),
					endpoint = is_endpoint,
					acl = [repr(i) for i in acl],
					inherit = inherit,
				))
		
		if not inherit:
			context.acl = list(self.base_policy)
		
		context.acl.extend((context.request.path, i, handler) for i in acl)
	
	def mutate(self, context, handler, args, kw):
		if not context.acl:
			if __debug__:
				log.debug("Skipping validation of empty ACL.", extra=dict(request=id(context)))
			
			return
		
		for path, predicate, handler in context.acl:
			result = predicate(context)
			if result is not None: break
		else:
			raise HTTPNotAuthorized("Authorization failure.")  # No rule matched.
		
		if not result:
			raise HTTPNotAuthorized("Authorization failure.")  # Rule matched, but said no.

