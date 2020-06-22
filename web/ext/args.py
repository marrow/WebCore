"""Argument handling extensions for WebCore applications.

These allow you to customize the behaviour of the arguments passed to endpoints.
"""

from itertools import chain
from inspect import getcallargs, getfullargspec, isroutine, ismethod
from re import compile as re, escape as rescape
from sys import flags
from warnings import warn

from webob.exc import HTTPBadRequest

from ..core.typing import Callable, Context, Iterable, Set, Tags, Optional, Pattern, PatternString, PatternStrings
from ..core.typing import PositionalArgs, KeywordArgs
from ..core.util import safe_name


log = __import__('logging').getLogger(__name__)  # A standard Python logger object.


class ArgumentExtension:
	"""Not for direct use."""
	
	@staticmethod
	def _process_flat_kwargs(source:dict, kwargs:KeywordArgs) -> None:
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
	def _process_rich_kwargs(source:dict, kwargs:KeywordArgs) -> None:
		"""Apply a nested structure to the current kwargs."""
		kwargs.update(source)


class StripArgumentsExtension:
	"""Always prevent certain named arguments from being passed to endpoints.
	
	Removals will be logged at the warning level in development mode, and at the debug level if Python is not invoked
	in developer mode. Running with optimizations enabled will automatically remove the logging overhead. If no
	patterns are defined explicitly, Google Analytics `utm_`-prefixed values will be stripped by default.
	"""
	
	last: bool = True
	provides: Tags = {'args.elision', 'kwargs.elision'}
	uses: Tags = {'timing.prefix'}
	
	strip: Pattern  # The patterns to search for removal, combined into one expression.
	
	def __init__(self, *patterns: PatternString) -> None:
		"""Identify specific arguments or name patterns to automatically remove."""
		
		if not patterns:
			patterns = (re("^utm_"), )
		
		encoded = ((i.pattern if isinstance(i, Pattern) else f"^{rescape(i)}$") for i in patterns)
		self.strip = re(f'({")|(".join(encoded)})')
	
	def collect(self, context:Context, endpoint:Callable, args:PositionalArgs, kw:KeywordArgs) -> None:
		strip, pattern = set(), self.strip
		
		for arg in kw:
			if pattern.search(arg):
				strip.add(arg)
		
		if strip and __debug__:
			(log.warning if flags.dev_mode else log.debug)(
					f"Eliding endpoint argument{'' if len(strip) == 1 else 's'}: {', '.join(sorted(strip))}",
					extra=dict(
							request = id(context),
							endpoint = safe_name(endpoint),
							endpoint_args = args,
							endpoint_kw = kw,
						))
		
		for arg in strip: del kw[arg]


class ValidateArgumentsExtension:
	"""Use this to enable validation of endpoint arguments.
	
	You can determine when validation is executed (never, always, or development) and what action is taken when a
	conflict occurs. Note that the default mode of operation is to only validate in development; impacting use "by
	name" within `extensions` during Application instantiation.
	"""
	
	__slots__ = ('collect', )
	
	always: bool = __debug__ or flags.dev_mode
	last: bool = True
	provides: Tags = {'args.validation', 'kwargs.validation'}
	uses: Tags = {'timing.prefix'}
	
	def __init__(self, enabled='development', correct=flags.dev_mode):
		"""Configure when validation is performed and the action performed.
		
		If `enabled` is `True` validation will always be performed, if `False`, never. If set to `development` the
		callback will not be assigned and no code will be executed per-request during production (optimized) runtime.
		
		When `correct` is falsy an `HTTPBadRequest` will be raised if a conflict occurs. If truthy the conflicting
		arguments are removed, with positional taking precedence to keyword. It is truthy by default when running in
		development mode.
		"""
		
		if enabled is True or (enabled == 'development' and __debug__):
			if correct:
				self.collect = self._correct
			else:
				self.collect = self._validate
	
	def _correct(self, context, endpoint, args, kw):
		if callable(endpoint) and not isroutine(endpoint):
			endpoint = endpoint.__call__  # Handle instances that are callable.
		
		spec = getfullargspec(endpoint)
		
		# First, process "positional arguments", typically consumed from unprocessed path elements.
		
		if not spec.varargs and len(args) > len(spec.args):
			if __debug__:
				difference = len(args) - len(spec.args)
				(log.warning if flags.dev_mode else log.debug)(
						f"Ignoring {difference} extraneous positional argument{'' if difference == 1 else 's'}.",
						extra=dict(
								request = id(context),
								endpoint = safe_name(endpoint),
							))
			
			del args[len(args):]
		
		matched = set(spec.args[:len(args)])  # Identify named arguments that have been populated positionally.
		
		# Next, we eliminate keyword arguments that would conflict with populated positional ones.
		
		conflicting = set()
		for key in matched.intersection(kw):
			conflicting.add(key)
			del kw[key]
		
		if conflicting and __debug__:
			plural = '' if len(conflicting) == 1 else 's'
			(log.warning if flags.dev_mode else log.debug)(
					f"Positional argument{plural} duplicated by name: {', '.join(sorted(conflicting))}",
					extra=dict(
							request = id(context),
							endpoint = safe_name(endpoint),
						))
		
		# Lastly, we remove any named arguments that don't exist as named arguments.
		
		allowable = set(chain(spec.args, spec.kwonlyargs))
		conflicting = set(kw).difference(allowable)
		
		for key in conflicting: del kw[key]
		
		if conflicting and __debug__:
			(log.warning if flags.dev_mode else log.debug)(
					f"Unknown named argument{'' if len(conflicting) == 1 else 's'}: {', '.join(sorted(conflicting))}",
					extra=dict(
							request = id(context),
							endpoint = safe_name(endpoint),
						))
	
	def _validate(self, context, endpoint, args, kw):
		try:
			if callable(endpoint) and not isroutine(endpoint):
				endpoint = endpoint.__call__  # Handle instances that are callable.
			
			getcallargs(endpoint, *args, **kw)
		
		except TypeError as e:
			# If the argument specification doesn't match, the handler can't process this request.
			# This is one policy. Another possibility is more computationally expensive and would pass only
			# valid arguments, silently dropping invalid ones. This can be implemented as a collection handler.
			log.error(str(e).replace(endpoint.__name__, safe_name(endpoint)), extra=dict(
					request = id(context),
					endpoint = safe_name(endpoint),
					endpoint_args = args,
					endpoint_kw = kw,
				))
			
			raise HTTPBadRequest("Incorrect endpoint arguments: " + str(e))


class ContextArgsExtension(ArgumentExtension):
	"""Add the context as the first positional argument, possibly conditionally."""
	
	always: bool = True
	first: bool = True
	provides: Tags = {'args.context'}
	
	def __init__(self, always=False):
		"""Configure the conditions under which the context is added to endpoint positional arguments.
		
		When `always` is truthy the context is always included, otherwise it's only included for callables that are
		not bound methods.
		"""
		self.always = always
	
	def collect(self, context, endpoint, args, kw):
		if not self.always:
			# Instance methods were handed the context at class construction time via dispatch.
			# The `not isroutine` bit here catches callable instances, a la "index.html" handling.
			if not isroutine(endpoint) or (ismethod(endpoint) and getattr(endpoint, '__self__', None) is not None):
				return
		
		args.insert(0, context)


class RemainderArgsExtension(ArgumentExtension):
	"""Add any unprocessed path segments as positional arguments."""
	
	always: bool = True
	first: bool = True
	needs: Tags = {'request'}
	uses: Tags = {'args.context'}
	provides: Tags = {'args', 'args.remainder'}
	
	def collect(self, context, endpoint, args, kw):
		if not context.request.remainder:
			return
		
		args.extend(i for i in context.request.remainder if i)


class QueryStringArgsExtension(ArgumentExtension):
	"""Add query string arguments ("GET") as keyword arguments."""
	
	always: bool = True
	first: bool = True
	needs: Tags = {'request'}
	provides: Tags = {'kwargs', 'kwargs.qs'}
	
	def collect(self, context, endpoint, args, kw):
		self._process_flat_kwargs(context.request.GET, kw)


class FormEncodedKwargsExtension(ArgumentExtension):
	"""Add form-encoded or MIME mmultipart ("POST") arguments as keyword arguments."""
	
	always: bool = True
	first: bool = True
	needs: Tags = {'request'}
	uses: Tags = {'kwargs.qs'}  # Query string values must be processed first, to be overridden.
	provides: Tags = {'kwargs', 'kwargs.form'}
	
	def collect(self, context, endpoint, args, kw):
		self._process_flat_kwargs(context.request.POST, kw)


class JSONKwargsExtension(ArgumentExtension):
	"""Add JSON-encoded arguments from the request body as keyword arguments.
	
	Deprecated in favour of generalized RESTful content negotiation via SerializationExtension. That extension will
	correctly handle error response if the body can not be decoded by any known handler, and generation of appropriate
	responses to deserialization failures.
	
	This is now a deprecation proxy shim which only depends on the serialization extension and emits a warning.
	"""
	
	needs: Tags = {'serialization'}
	provides: Tags = {'kwargs', 'kwargs.json'}
	
	def __init__(self):
		warn("Use of specialized JSONKwargsExtension is deprecated; SerializationExtension enabled instead.",
				DeprecationWarning)
