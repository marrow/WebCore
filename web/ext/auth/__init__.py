# encoding: utf-8

from functools import partial, wraps
from collections import MutableMapping

from marrow.package.loader import traverse, load
from webob.exc import HTTPUnauthorized

from web.ext.auth import predicate


class AuthenticationExtension(object):
	"""WebCore authentication services.
	
	Note: use of the rich Rule objects requires the `marrow.schema` package.  Basic predicates do not.
	
	This extension handles three different aspects of authentication and authorization:
	
	* Authentication - Identifying the currently logged in user.  This can operate as a stack, allowing for
	  `sudo`-like behavior.
	
	* Predicate Authorization - Using simple rules to identify authorization failures.
	
	* ACL Authorization - A rich rule-based way of granting or denying access.  Rules are automatically collected
	  as dispatch descends from object to object via the `__acl__` attribute or dictionary value, and evaluated prior
	  to execution of the end-point.  Inheritance of rules is controllable using the value of `__acl_inherit__`.
	
	The following values are added to the context, and thus `web` template namespace:
	
	* `user` - An object representing the current user.
	* `acl` - ACL rules currently selected for evaluation.
	
	ACL rules can be any callable accepting an execution context and returning `True` (allow access), `False` (deny
	access), or `None` (rule does not apply).  The first rule returning a non-`None` value completes evaluation.
	
	Basic predicates are actually ACL rules, often registered against a given object using the `rule` decorator.
	
	By default access to methods is granted.  If any rule or predicate is registered the default changes to deny.
	"""
	
	__slots__ = ('_lookup', '_authenticate', 'key')
	
	uses = ['template']
	needs = ['session']
	provides = ['auth', 'authentication', 'identity', 'acl']
	
	def __init__(self, lookup, authenticate, key='user'):
		self._lookup = load(lookup, 'web.auth.lookup')
		self._authenticate = load(authenticate, 'web.auth.authenticate')
		self.key = key
		
		
		super(AuthenticationExtension, self).__init__()
	
	def prepare(self, context):
		"""Prepare context variables."""
		
		context.acl = []
		
		context.authenticate = partial(self.authenticate, context)
		context.deauthenticate = partial(self.authenticate, context)
		
		identifier = context.session.get(self.key, None)
		
		if not identifier:
			context.user = None
		else:
			context.user = self._lookup(identifier)
		
		# context.log = context.log.data(user=context.user)
	
	def dispatch(self, context, consumed, handler, is_endpoint):
		"""Automatically combine ACL rules as we descend through objects."""
		
		if not traverse(handler, '__acl_inherit__', True, protect=False):
			del context.acl[:]
		
		context.acl.extend(traverse(handler, '__acl__', [], protect=False))
	
	def before(self, context):
		"""Validate the ACL."""
		
		if not context.acl:
			# Exit early (allow access) if no rules are defined.
			return
		
		for rule in context.acl:
			result = rule(context)
			
			if result is None:
				# Rule doesn't apply to this request.
				continue
			
			if not result:
				raise HTTPUnauthorized()
			
			return
		
		raise HTTPUnauthorized()
	
	def authenticate(self, context, identifier, password=None, force=False):
		"""Authenticate a user.
		
		Sets the current user in the session.  You can optionally omit a password
		and force the authentication to authenticate as any user.
		
		If successful, the web.auth.user variable is immediately available.
		
		Returns True on success, False otherwise.
		"""
		
		if force:
			result = (identifier, self._lookup(identifier))
		else:
			result = self._authenticate(identifier, password)
		
		if result is None or result[1] is None:
			return False
		
		context.session[self.key] = result[0]
		context.session.save()
		
		context.user = result[1]
		
		return True
	
	def deauthenticate(self, context, nuke=False):
		"""Force logout.
		
		The web.auth.user variable is immediately deleted and session variable cleared.
		
		Additionally, this function can also completely erase the Beaker session.
		"""
		
		context.user = None
		
		session = context.session
		
		if nuke:
			session.invalidate()
		
		session[self.key] = None
		
		if not session.autocommit:
			session.save()


def rule(*rules, **kw):
	"""Decorator to assign ACL rules to a given class or method.
	
	Returns the original object after annotation.  Positional arguments represent rules and the `inherit` keyword
	argument can be used to prevent inheritance of parent rules.  May be called several times against the same object.
	"""
	
	inherit = kw.pop('inherit', True)
	
	if kw:
		raise TypeError("rule decorator got unexpected keyword arguments: " + ', '.join(kw))
	
	def decorator(obj):
		if isinstance(obj, MutableMapping):
			if '__acl__' not in obj:
				obj['__acl__'] = []
			
			obj['__acl__'].extend(rules)
			obj['__acl_inherit__'] = inherit
			
		else:
			if not hasattr(obj, '__acl__'):
				obj.__acl__ = []
			
			obj.__acl__.extend(rules)
			obj.__acl_inherit__ = inherit
		
		return obj
	
	return decorator
