# encoding: utf-8

"""Argument handling extensions for WebCore applications.

These allow you to customize the behaviour of the arguments passed to endpoints.
"""

from inspect import isroutine, ismethod, getcallargs

from webob.exc import HTTPNotFound
from web.core.util import safe_name


# A standard Python logger object.
log = __import__('logging').getLogger(__name__)


class ArgumentExtension(object):
	"""Not for direct use."""
	
	@staticmethod
	def _process_flat_kwargs(source, kwargs):
		"""Apply a flat namespace transformation to recreate (in some respects) a rich structure.
		
		This applies several transformations, which may be nested:
		
		`foo` (singular): define a simple value named `foo`
		`foo` (repeated): define a simple value for placement in an array named `foo`
		`foo[]`: define a simple value for placement in an array, even if there is only one
		`foo.<id>`: define a simple value to place in the `foo` array at the identified index
		
		By nesting, you may define deeper, more complex structures:
		
		`foo.bar`: define a value for the named element `bar` of the `foo` dictionary
		`foo.<id>.bar`: define a `bar` dictionary element on the array element marked by that ID
		
		References to `<id>` represent numeric "attributes", which makes the parent reference be treated as an array,
		not a dictionary. Exact indexes might not be able to be preserved if there are voids; Python lists are not
		sparse.
		
		No validation of values is performed.
		"""
		
		ordered_arrays = []
		
		# Process arguments one at a time and apply them to the kwargs passed in.
		
		for name, value in source.items():
			container = kwargs
			
			if '.' in name:
				parts = name.split('.')
				name = name.rpartition('.')[2]
				
				for target, following in zip(parts[:-1], parts[1:]):
					if following.isnumeric():  # Prepare any use of numeric IDs.
						container.setdefault(target, [{}])
						if container[target] not in ordered_arrays:
							ordered_arrays.append(container[target])
						container = container[target][0]
						continue
					
					container = container.setdefault(target, {})
			
			if name.endswith('[]'):  # `foo[]` or `foo.bar[]` etc.
				name = name[:-2]
				container.setdefault(name, [])
				container[name].append(value)
				continue
			
			if name.isnumeric() and container is not kwargs:  # trailing identifiers, `foo.<id>`
				container[int(name)] = value
				continue
			
			if name in container:
				if not isinstance(container[name], list):
					container[name] = [container[name]]
				
				container[name].append(value)
				continue
			
			container[name] = value
		
		for container in ordered_arrays:
			elements = container[0]
			del container[:]
			container.extend(value for name, value in sorted(elements.items()))
	
	@staticmethod
	def _process_rich_kwargs(source, kwargs):
		"""Apply a nested structure to the current kwargs."""
		kwargs.update(source)


class ValidateArgumentsExtension(object):
	"""Use this to enable validation of endpoint arguments.
	
	You can determine when validation is executed (never, always, or development) and what action is taken when a
	conflict occurs.
	"""
	
	last = True
	
	provides = {'args.validation', 'kwargs.validation'}
	
	def __init__(self, enabled='development', correct=False):
		"""Configure when validation is performed and the action performed.
		
		If `enabled` is `True` validation will always be performed, if `False`, never. If set to `development` the
		callback will not be assigned and no code will be executed during runtime.
		
		When `correct` is falsy (the default), an `HTTPNotFound` will be raised if a conflict occurs. If truthy the
		conflicting arguments are removed, with positional taking precedence to keyword.
		"""
		
		if enabled is True or (enabled == 'development' and __debug__):
			self.mutate = self._mutate
	
	def _mutate(self, context, endpoint, args, kw):
		try:
			if callable(endpoint) and not isroutine(endpoint):
				endpoint = endpoint.__call__  # Handle instances that are callable.
			
			getcallargs(endpoint, *args, **kw)
		
		except TypeError as e:
			# If the argument specification doesn't match, the handler can't process this request.
			# This is one policy. Another possibility is more computationally expensive and would pass only
			# valid arguments, silently dropping invalid ones. This can be implemented as a mutate handler.
			log.error(str(e).replace(endpoint.__name__, safe_name(endpoint)), extra=dict(
					request = id(context),
					endpoint = safe_name(endpoint),
					endpoint_args = args,
					endpoint_kw = kw,
				))
			
			raise HTTPNotFound("Incorrect endpoint arguments: " + str(e))


class ContextArgsExtension(ArgumentExtension):
	"""Add the context as the first positional argument, possibly conditionally."""
	
	first = True
	provides = {'args.context'}
	
	def __init__(self, always=False):
		"""Configure the conditions under which the context is added to endpoint positional arguments.
		
		When `always` is truthy the context is always included, otherwise it's only included for callables that are
		not bound methods.
		"""
		self.always = always
	
	def mutate(self, context, endpoint, args, kw):
		if not self.always:
			# Instance methods were handed the context at class construction time via dispatch.
			# The `not isroutine` bit here catches callable instances, a la "index.html" handling.
			if not isroutine(endpoint) or (ismethod(endpoint) and getattr(endpoint, '__self__', None) is not None):
				return
		
		args.insert(0, context)


class RemainderArgsExtension(ArgumentExtension):
	"""Add any unprocessed path segments as positional arguments."""
	
	first = True
	needs = {'request'}
	uses = {'args.context'}
	provides = {'args.remainder'}
	
	def mutate(self, context, endpoint, args, kw):
		if not context.request.remainder:
			return
		
		args.extend(context.request.remainder)


class QueryStringArgsExtension(ArgumentExtension):
	"""Add query string arguments ("GET") as keyword arguments."""
	
	first = True
	needs = {'request'}
	provides = {'kwargs.get'}
	
	def mutate(self, context, endpoint, args, kw):
		self._process_flat_kwargs(context.request.GET, kw)


class FormEncodedKwargsExtension(ArgumentExtension):
	"""Add form-encoded or MIME mmultipart ("POST") arguments as keyword arguments."""
	
	first = True
	needs = {'request'}
	uses = {'kwargs.get'}  # Query string values must be processed first, to be overridden.
	provides = {'kwargs.post'}
	
	def mutate(self, context, endpoint, args, kw):
		self._process_flat_kwargs(context.request.POST, kw)


class JSONKwargsExtension(ArgumentExtension):
	"""Add JSON-encoded arguments from the request body as keyword arguments."""
	
	first = True
	needs = {'request'}
	uses = {'kwargs.get'}  # We override values defined in the query string.
	provides = {'kwargs.json'}
	
	def mutate(self, context, endpoint, args, kw):
		if not context.request.content_type == 'application/json':
			return
		
		if not context.request.body:
			return
		
		self._process_rich_kwargs(context.request.json, kw)


