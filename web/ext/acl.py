# encoding: utf-8

"""Access Control List Security Extension

Predicate-based security for your applications, extensions, and reusable components.

* This extension is **available in**: `WebCore>=2.0.3,<2.1.0`
* This extension **requires [Python 3](https://www.python.org/)**.
* This extension has **no external package dependencies**.
* This extension is **available with the name** `acl` in the `web.ext` namespace.
* This extension adds the following **context attributes**:
	* `acl`
* This extension uses **namespaced plugins** from:
	* `web.acl.predicate`

1. [**Introduction**](#introduction)
	2. [Operation](#operation)
	3. [Predicates](#predicates)
2. [**Usage**](#usage)
	1. [Enabling the Extension](#enabling-the-extension)
		1. [_Imperative Configuration_](#imperative-configuration)
		2. [_Declarative Configuration_](#declarative-configuration)
	2. [Defining ACLs](#defining-acls)
		1. [_Explicit Usage_](#explicit-usage)
		2. [_Decoration_](#decoration)
		3. [_Endpoint Return Values_](#endpoint-return-values)


# Introduction

This extension provides a method of collecting rules from objects during dispatch descent and subsequently evaluating
them. This serves the purpose of an access cotrol list (ACL) by allowing these rules to grant access (return `True`),
explicitly deny access (return `False`), or abstain (return `None`). Additionally, values returned from endpoints will
have the value of their `__acl__` attribute evaluated, if present.

Also provided are a stock set of _predicates_ which allow for basic boolean logic, various nesting patterns, and
provide building blocks for more complex behaviour. It is preferred to access these via the `where` helper object,
whose attributes (also provided as a mapping) are the names of `entry_points` registered plugins.


## Operation

On any endpoint or object leading to an endpoint during _dispatch_, define an `__acl__` attribute or property which
provides an iterable (`set`, `list`, `tuple`, generator, etc.) of _predicate_ objects. Objects may also optionally
specify an `__acl_inherit__` attribute or property, which, if _falsy_, will clear the ACL that had been built so far
for the request.

After a final endpoint has been reached, these rules are evaluated in turn (using the `First` predicate), passing the
request context as their first argument.  Each is called until one either returns `True` to indicate permission has
been explicitly granted, or returns `False` to indicate permission has been explicitly denied. If no predicates decide
to have an opinion, the default action is configurable.


## Predicates

A _predicate_ is any callable object that optionally accepts a context as its first positional parameter. One might
look like:

```python
def always(context=None):
	return True
```

That's it, really. The provided built-in ones are class-based, but the process is the same even if the method has a
strange name like `__call__`.


# Usage

## Enabling the Extension

Before utilizing access control list functionality in your own application you must first enable the extension.

Regardless of configuration route chosen rules may be specified as strings, classes, or callables. Strings are
resolved using the `web.acl.predicate` `entry_point` namespace and further processed. Classes (either directly, or
loaded by plugin name) are instantiated without arguments and their instance used.


### Imperative Configuration

Applications using code to explicitly construct the WebCore `Application` object, but with no particular custom base
ruleset needed, can pass the extension by name. It will be loaded using its `entry_points` plugin reference.

```python
app = Application("Hi.", extensions=['acl'])
```

Applications with a more strict configuration may wish to specify a default rule of `never`. Import the extension
yourself, and specify a default rule.

```python
from web.ext.acl import ACLExtension, when

app = Application("Hi.", extensions=[ACLExtension(default=when.never)])
```

More complex arrangements can be had by specifying rules positionally (their order will be preserved) or by passing a
`policy` iterable by name. These may be combined with the `default` named argument, with them being combined as
`positional` + `policy` + `default`.


### Declarative Configuration

Using a JSON or YAML-based configuration, you would define your application's `extensions` section either with the
bare extension declared:

```yaml
application:
	root: "Hi."
	
	extensions:
		acl:
```

Or, specify a default policy by treating the `acl` entry as an array:

```yaml
application:
	root: "Hi."
	
	extensions:
		acl:
			- never
```

By specifying a singular `default` explicitly:

```yaml
application:
	root: "Hi."
	
	extensions:
		acl:
			default: never
```

Or, finally, by specifying the `policy`, which must be an array, explicitly:

```yaml
application:
	root: "Hi."
	
	extensions:
		acl:
			policy:
				- never
```

Use of `policy` and `default` may be combined, with the default appended to the given policy.


## Defining ACLs

Note: We'll be using [object dispatch](https://github.com/marrow/web.dispatch.object/) for these examples.

First, you're going to need to `from web.ext.acl import when` to get easy access to predicates.


### Explicit Usage

Define an iterable of predicates using the `__acl__` attribute.

```python
class PermissiveController:
	__acl__ = [when.always]
	
	def __init__(self, context):
		pass
	
	def __call__(self):
		return "Hi."
```

For intermediary nodes in descent and return values, such as a "root controller with method" arrangement, you can
define an `__acl__` attribute. The contents of this attribute is collected during processing of dispatch events.


### Decoration

Using the `when` utility as a decorator or decorator generator.

```python
@when(when.never)
class SecureController:
	def __init__(self, context):
		pass
	
	@when(when.always, inherit=False)
	def insecure_resource(self):
		return "Yo."
	
	def __call__(self):
		return "Hi."
```

You can use the `when` predicate accessor as a decorator, defining the predicates for an object as positional
parameters.  The result of calling `when` can be saved used later as a decorator by itself, or as a filter to set that
attribute on other objects.


### Endpoint Return Values

Controlling access to information, not just endpoints.

```python
class Thing:
	__acl__ = [when.never]


def endpoint(context):
	return Thing()
```

In this example, `Thing` will not allow itself to be returned by an endpoint. This process is not recursive.


# Extending

Defining new predicates is fairly straightforward given the very simple interface. However, because many demands of
predicates can be resolved entirely by comparison against a value from the request context, two predicate factories
are provided. These can be used on-demand, or the result can be saved for repeated use later.


### Context Value Matches

Grant or deny access based on a value from the context matching one of several possible values.

```python
deny_console = when.matches(False, 'request.client_addr', None)
local = when.matches(True, 'request.remote_addr', '127.0.0.1', '::1')

@when(deny_console, local, when.matches(True, 'user.admin', True))
def endpoint(context):
	return "Hi."
```

This will grant access to local users and those with the `user.admin` flag equal to `True`, as retrieved from the
context. The `local` predicate has been saved for subsequent use, and demonstrates comparing against any of a number
of allowable values. The first argument is the intended predicate result if a match is made, the second is the value
to traverse and compare, and any remaining arguments are treated as acceptable values.


### Context Value Contains

Grant or deny access based on a value from the context containing one of several possible values.

```python
role = when.contains.partial(True, 'user.role')

@when(role('admin', 'editor'))
def endpoint(context):
	return "Hi."
```

This allows you to easily compare against containers such as lists and sets. Also demonstrataed is the ability to
"partially apply" a predicate, that is, apply some arguments, then apply the rest later.
"""

# ## Imports

from __future__ import unicode_literals

from weakref import proxy
from functools import partial
from itertools import chain
from inspect import isclass
from webob.exc import HTTPForbidden
from marrow.package.host import PluginManager
from marrow.package.loader import traverse

from web.core.util import safe_name
from web.core.compat import Path


# ## Module Globals

log = __import__('logging').getLogger(__name__)

if __debug__:  # Documentation helpers.
	__doc_groups__ = {  # Map collapsable sections.
				'Imperative Configuration': {'config', 'choice'},
				'Declarative Configuration': {'config', 'choice'},
				'Explicit Usage': {'sample', 'captioned'},
				'Decoration': {'sample', 'captioned'},
				'Endpoint Return Values': {'sample', 'captioned'},
				'Context Value Matches': {'sample', 'captioned'},
				'Context Value Contains': {'sample', 'captioned'},
			}


# ## Plugin Manager and Decorator

class _When(PluginManager):
	"""A derivative of a PluginManager that acts as a decorator.
	
	Will assign the `__acl__` property as the tuple of arguments passed.
	"""
	def __call__(self, *acl, **kw):
		inherit = kw.pop('inherit', True)
		
		if __debug__:
			if kw:  # This is the only keyword argument we accept.
				raise TypeError("Unknown keyword arguments: " + ", ".join(sorted(kw)))
		
		def acl_when_inner(target):
			if acl:
				target.__acl__ = acl
			
			if not inherit:
				target.__acl_inherit__ = False
			
			return target
		
		return acl_when_inner

when = _When('web.acl.predicate')  # Easy reference by short name, e.g. when.match(...)


# ## ACL Evaluation Result and ACL List Abstractions

class ACLResult(object):
	__slots__ = ('result', 'predicate', 'path', 'source')
	
	def __init__(self, result, predicate, path=None, source=None):
		self.result = result
		self.predicate = predicate
		self.path = path
		self.source = source
	
	def __bool__(self):
		return bool(self.result)
	
	__nonzero__ = __bool__


class ACL(list):
	def __init__(self, *rules, **kw): # Python 3: , context=None, policy=None):
		super(ACL, self).__init__((None, rule, None) for rule in rules)
		
		context = kw.pop('context', None)
		policy = kw.pop('policy', None)
		
		if __debug__:
			if kw:  # This is the only keyword argument we accept.
				raise TypeError("Unknown keyword arguments: " + ", ".join(sorted(kw)))
		
		self.context = proxy(context) if context else None
		self.policy = policy or ()
	
	@property
	def is_authorized(self):
		for path, predicate, source in self:
			result = predicate() if self.context is None else predicate(self.context)
			
			if __debug__:
				log.debug(repr(predicate) + " (from " + repr(source) + ") voted " + repr(result))
			
			if result is None:
				continue
			
			return ACLResult(result, predicate, path, source)
		
		return ACLResult(None, None, None, None)
	
	def __bool__(self):
		return bool(len(self) or len(self.policy))
	
	__nonzero__ = __bool__
	
	def __iter__(self):
		return chain(super(ACL, self).__iter__(), ((None, i, None) for i in self.policy))
	
	def __repr__(self):
		return '[' + ', '.join(repr(i) for i in self) + ']'


# ## Simple Predicates

class Predicate(object):
	__slots__ = ()
	
	def __call__(self, context=None):
		raise NotImplementedError()
	
	@classmethod
	def partial(cls, *args, **kw):
		"""Retrieve a partially applied constructor for this predicate."""
		return partial(cls, *args, **kw)


class Not(Predicate):
	"""Invert the meaning of another predicate."""
	
	__slots__ = ('predicate', )
	
	def __init__(self, predicate):
		self.predicate = predicate
	
	def __call__(self, context=None):
		result = self.predicate(context) if context else self.predicate()
		
		if result is None:
			return
		
		return not result


class Always(Predicate):
	"""Always grant access."""
	
	__slots__ = ()
	
	def __call__(self, context=None):
		return True

always = Always()  # Convienent singleton to use.


class Never(Predicate):
	"""Always deny access."""
	
	__slots__ = ()
	
	def __call__(self, context=None):
		return False

never = Never()  # Convienent singleton to use.


class First(Predicate):
	"""Authorizes or denies an action on the first non-veto predicate."""
	
	__slots__ = ('predicates', )
	
	def __init__(self, *predicates):
		self.predicates = predicates
	
	def __call__(self, context=None):
		for predicate in self.predicates:
			result = predicate(context) if context else predicate()
			
			if result is None:  # Abstain
				continue
			
			return bool(result)


class All(Predicate):
	"""Authorizes an action only if all predicates authorize the action.
	
	Returns `False` on first failure, `True` if all voting predicates returned `True`, `None` otherwise.
	"""
	
	__slots__ = ('predicates', )
	
	def __init__(self, *predicates):
		self.predicates = predicates
	
	def __call__(self, context=None):
		if context:
			results = (predicate(context) for predicate in self.predicates)
		else:
			results = (predicate() for predicate in self.predicates)
		
		vote = None
		
		for result in results:
			if result is None:  # Abstain
				continue
			
			if not bool(result):  # Exit Early
				return False
			
			vote = True
		
		return vote


class Any(Predicate):
	"""Authorize an action if any predicate authorizes the action.
	
	Returns `True` on first success, `False` if all voting predicates returned `False`, `None` otherwise.
	"""
	
	__slots__ = ('predicates', )
	
	def __init__(self, *predicates):
		self.predicates = predicates
	
	def __call__(self, context=None):
		if context:
			results = (predicate(context) for predicate in self.predicates)
		else:
			results = (predicate() for predicate in self.predicates)
		
		vote = None
		
		for result in results:
			if result is None:  # Abstain
				continue
			
			if bool(result):
				return True
			
			vote = False
		
		return vote


class ContextMatch(Predicate):
	"""Match a variable from the context to one of a set of candidate values.
	
	As per most non-base predicates, this accepts a `grant` value determining if a match should be considered success
	(`True`) or not (`False`), then the attribute to attempt to look up, which may be deep or contain array
	references (see the `traverse` function from the `marrow.package.loader` package), and one or more values to
	consider as a match. In the event the attribute can not be loaded, the `default` (which must be passed as a
	keyword argument) will be used, `None` by default.
	
	Examples might include:
	
	admin = ContextMatch(True, 'user.admin', True)
	local = ContextMatch(True, 'request.remote_addr', '127.0.0.1', '::1')
	"""
	
	__slots__ = ('grant', 'attribute', 'values', 'default')
	SENTINEL = object()  # A singleton used internally for comparison.
	
	def __init__(self, grant, attribute, *values, **kw):
		default = kw.pop('default', None)
		
		if __debug__:
			if kw:  # This is the only keyword argument we accept.
				raise TypeError("Unknown keyword arguments: " + ", ".join(sorted(kw)))
			
			if not values:
				raise TypeError("You must supply one or more values to compare against.")
			
			if grant not in (True, False):
				raise ValueError("The `grant` argument must be `True` (allow) or `False` (deny).")
			
			if default not in (None, True, False):
				raise ValueError("The default may either be `True` (allow), `False` (deny), or `None` (abstain).")
		
		self.grant = grant  # True if we grant access, False if we deny access.
		self.attribute = attribute  # The attribute to retrieve, i.e. "user.admin"
		self.values = values
		self.default = default
	
	def __call__(self, context):
		value = traverse(context, self.attribute, self.SENTINEL)  # Retrieve the value.
		
		if value is self.SENTINEL:
			return self.default
		
		result = any(i == value for i in self.values)  # We do this rather than "in" to support equality comparison.
		
		return self.grant if result else None


class ContextContains(ContextMatch):
	"""Match a variable from the context containing one or more values.
	
	Similar to ContextMatch, except matches the values being "in" the target variable rather than comparing equality.
	
	Examples might include:
	
	reviewer = ContextContains(True, 'user.role', 'reviewer')
	"""
	
	__slots__ = ('grant', 'attribute', 'values', 'default')
	
	def __call__(self, context):
		value = traverse(context, self.attribute, self.SENTINEL)  # Retrieve the value.
		
		if value is self.SENTINEL:
			return self.default
		
		result = any(i in value for i in self.values)
		
		return self.grant if result else None


# ## Extension

class ACLExtension(object):
	"""Access control list extension.
	
	Predicates are gathered as dispatch descends through objects, collecting them from the `__acl__` attribute.
	If any object defines `__acl_inherit__` as a falsy value the ACL gathered so far is cleared before continuing.
	"""
	
	provides = {'acl'}
	extensions = {'web.acl.predicate'}
	context = {'acl'}
	
	def __init__(self, *_policy, **kw): # Python 3: , default=None, policy=None):
		"""Configure the ACL extension by defining an optional base policy.
		
		This policy will be used as the base for every request; these are evaluated first, always.
		"""
		
		default = kw.pop('default', None)
		policy = kw.pop('policy', None)
		
		if __debug__:
			if kw:  # This is the only keyword argument we accept.
				raise TypeError("Unknown keyword arguments: " + ", ".join(sorted(kw)))
		
		if policy is None:
			policy = []
		
		if _policy:
			policy = chain(_policy, policy)
		
		policy = (when[rule] if isinstance(rule, str) else rule for rule in policy)
		policy = (rule() if isclass(rule) else rule for rule in policy)
		
		policy = self.policy = list(policy)
		
		if default:
			policy.append(default)
		
		log.info("ACL extension prepared with defualt policy: " + repr(policy))
	
	# ### Request-Level Callbacks
	
	def prepare(self, context):
		"""Called to prepare the request context by adding an `acl` attribute."""
		
		if __debug__:
			log.debug("Preparing request context with ACL.", extra=dict(request=id(context)))
		
		context.acl = ACL(context=context, policy=self.policy)
	
	def dispatch(self, context, consumed, handler, is_endpoint):
		"""Called as dispatch descends into a tier.
		
		The ACL extension uses this to build up the current request's ACL.
		"""
		
		acl = getattr(handler, '__acl__', ())
		inherit = getattr(handler, '__acl_inherit__', True)
		
		if __debug__:
			log.debug("Handling dispatch event: " + repr(handler) + " " + repr(acl), extra=dict(
					request = id(context),
					consumed = consumed,
					handler = safe_name(handler),
					endpoint = is_endpoint,
					acl = [repr(i) for i in acl],
					inherit = inherit,
				))
		
		if not inherit:
			if __debug__:
				log.debug("Clearing collected access control list.")
			
			del context.acl[:]
		
		context.acl.extend((Path(context.request.path), i, handler) for i in acl)
	
	def mutate(self, context, handler, args, kw):
		if not context.acl:
			if __debug__:
				log.debug("Skipping validation of empty ACL.", extra=dict(request=id(context)))
			
			return
		
		grant = context.acl.is_authorized
		
		if grant.result is False:
			log.error("Endpoint authorization failed: " + repr(grant), extra=dict(
					grant = False,
					predicate = repr(grant.predicate) if grant.predicate else None,
					path = str(grant.path) if grant.path else None,
					source = safe_name(grant.source) if grant.source else None
				))
			raise HTTPForbidden()
		
		elif __debug__:
			log.debug("Successful endpoint authorization: " + repr(grant), extra=dict(
					grant = False,
					predicate = repr(grant.predicate) if grant.predicate else None,
					path = str(grant.path) if grant.path else None,
					source = safe_name(grant.source) if grant.source else None
				))
	
	def transform(self, context, handler, result):
		try:
			acl = result.__acl__
		except AttributeError:
			return result
		
		acl = ACL(*acl, context=context)
		valid = acl.is_authorized
		
		if valid.result is False:
			log.error("Response rejected due to return value authorization failure.", extra=dict(
					grant = False,
					predicate = repr(valid.predicate) if valid.predicate else None,
					path = str(valid.path) if valid.path else None,
					result = safe_name(type(result))
				))
			return HTTPForbidden()
		
		elif __debug__:
			log.debug("Successful response authorization.", extra=dict(
					grant = valid.result,
					predicate = repr(valid.predicate) if valid.predicate else None,
					path = str(valid.path) if valid.path else None,
					result = safe_name(type(result))
				))
		
		return result

