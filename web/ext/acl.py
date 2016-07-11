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
from marrow.package.loader import traverse

from web.core.util import safe_name


# ## Module Globals

log = __import__('logging').getLogger(__name__)


# ## Simple Predicates

class Predicate(object):
	def __init__(self):
		raise NotImplementedError()
	
	def __call__(self, context):
		raise NotImplementedError()


def Not(Predicate):
	"""Invert the meaning of another predicate."""
	
	__slots__ = ('predicate', )
	
	def __init__(self, predicate):
		self.predicate = predicate
	
	def __call__(self, context):
		result = self.predicate(context)
		
		if result is None:
			return
		
		return not result


class All(Predicate):
	"""Authorizes an action only if all predicates authorize the action."""
	
	__slots__ = ('predicates', )
	
	def __init__(self, *predicates):
		self.predicates = predicates
	
	def __call__(self, context):
		return all(predicate(context) for predicate in self.predicates)


class Any(Predicate):
	"""Authorize an action if any predicate authorizes the action."""
	
	__slots__ = ('predicates', )
	
	def __init__(self, *predicates):
		self.predicates = predicates
	
	def __call__(self, context):
		return any(predicate(context) for predicate in self.predicates)


class ContextMatch(Predicate):
	"""Match a variable from the context to one of a set of candidate values.
	
	As per most non-base predicates, this accepts a `grant` value determining if a match should be considered success
	(`True`) or not (`False`), then the attribute to attempt to look up, which may be deep or contain array
	references (see the `traverse` function from the `marrow.package.loader` package), and one or more values to
	consider as a match. In the event the attribute can not be loaded, the `default` (which must be passed as a
	keyword argument) will be used, `None` by default.
	
	Examples might include:
	
	local = ContextMatch(True, 'request.remote_addr', '127.0.0.1')
	admin = ContextMatch(True, 'user.admin', True)
	"""
	
	__slots__ = ('grant', 'attribute', 'values', 'default')
	SENTINEL = object()  # A singleton used internally for comparison.
	
	def __init__(self, grant, attribute, *values, **kw):
		default = kw.pop('default', None)
		
		if kw:  # This is the only keyword argument we accept.
			raise TypeError()
		
		assert grant in (True, False), "The `grant` argument must be True (allow) or False (deny).`"
		
		self.grant = grant  # True if we grant access, False if we deny access.
		self.attribute = attribute  # The attribute to retrieve, i.e. "user.admin", or "
		self.values = values
		self.default = default
	
	def __call__(self, context):
		try:
			value = traverse(context, self.attribute, self.SENTINEL)  # Retrieve the value.
		except LookupError:
			value = self.SENTINEL
		
		if value is self.SENTINEL:
			return self.default
		
		result = any(i == value for i in self.values)  # We do this rather than "in" to support equality comparison.
		return self.grant if result else not self.grant


class ContextIn(ContextMatch):
	"""Match a variable from the context containing one or more values.
	
	Similar to ContextMatch, except matches the values being "in" the target variable rather than comparing equality.
	"""
	
	__slots__ = ('grant', 'attribute', 'values', 'default')
	
	def __call__(self, context):
		try:
			value = traverse(context, self.attribute, self.SENTINEL)  # Retrieve the value.
		except LookupError:
			value = self.SENTINEL
		
		if value is self.SENTINEL:
			return self.default
		
		try:
			return any(i in value for i in self.values)
		except TypeError:
			return self.default


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

