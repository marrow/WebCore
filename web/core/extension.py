# encoding: utf-8

"""WebCore extension management.

This extension registry handles loading and access to extensions as well as the collection of standard WebCore
Extension API callbacks. Reference the `SIGNALS` constant for a list of the individual callbacks that can be
utilized and their meanings, and the `extension.py` example for more detailed descriptions.

At a basic level an extension is a class. That's it; attributes and methods are used to inform the manager
of extension metadata and register callbacks for certain events. The most basic extension is one that does
nothing:

	class Extension: pass

To register your extension, add a reference to it to your project's `entry_points` in your project's `setup.py`
under the `web.extension` namespace:

	setup(
		...,
		entry_points = {'web.extension': [
				'example = myapp:Extension',
			]},
	)

Your extension may define several additional properties:

* `provides` -- declare a set of tags describing the features offered by the plugin
* `needs` -- delcare a set of tags that must be present for this extension to function
* `uses` -- declare a set of tags that must be evaluated prior to this extension, but aren't hard requirements
* `first` -- declare that this extension is a dependency of all other non-first extensions if truthy
* `last` -- declare that this extension depends on all other non-last extensions if truthy
* `signals` -- a set of additional signal names declared used (thus cacheable) by the extension manager

Tags used as `provides` values should also be registered as `web.extension` entry points. Additional `signals` may be
prefixed with a minus symbol (-) to request reverse ordering, simulating the exit path of WSGI middleware.

"""

# ## Imports

from __future__ import unicode_literals

from marrow.package.host import ExtensionManager

from .compat import items
from .context import Context


# ## Module Globals

# A standard Python logger object.
log = __import__('logging').getLogger(__name__)


# ## Extension Manager

class WebExtensions(ExtensionManager):
	"""Principal WebCore extension manager."""
	
	# Each of these is an optional extension callback attribute.
	SIGNALS = {  # Core extension hooks.
			'start',  # Executed during Application construction.
			'stop',  # Executed when (and if) the serve() server returns.
			'graceful',  # Executed when (and if) the process is instructed to reload configuration.
			'prepare',  # Executed during initial request processing.
			'dispatch',  # Executed once for each dispatch event.
			'before',  # Executed after all extension `prepare` methods have been called, prior to dispatch.
			'mutate',  # Inspect and potentially mutate arguments to the handler prior to execution.
			'-after',  # Executed after dispatch has returned and the response populated.
			'-transform',  # Transform the result returned by the handler and apply it to the response.
			'-done',  # Executed after the response has been consumed by the client.
			'-middleware',  # Executed to allow WSGI middleware wrapping.
		}
	
	__isabstractmethod__ = False  # Work around a Python 3.4+ issue when attaching to the context.
	
	# ### \_\_init__(ctx: _ApplicationContext_)
	def __init__(self, ctx):
		"""Extension registry constructor.
		
		The extension registry is not meant to be instantiated by third-party software. Instead, access the registry
		as an attribute of the current Application or Request context: `context.extension`
		
		Currently, this uses some application-internal shenanigans to construct the initial extension set.
		"""
		
		self.feature = set()  # Track the active `provides` tags.
		all = self.all = self.order(ctx.app.config['extensions'])  # Dependency ordered, active extensions.
		
		signals = {}
		inverse = set()
		
		# Prepare the known callback sets.
		
		def add_signal(name):
			if name[0] == '-':
				name = name[1:]
				inverse.add(name)
			
			signals[name] = []
		
		# Populate the initial set of signals from our own.
		for signal in self.SIGNALS: add_signal(signal)
		
		# Populate additional signals and general metadata provided by registered extensions.
		for ext in all:
			self.feature.update(getattr(ext, 'provides', []))  # Enable those flags.
			for signal in getattr(ext, 'signals', []): add_signal(signal)  # And those callbacks.
		
		# Prepare the callback cache.
		
		for ext in all:
			for signal in signals:  # Attach any callbacks that might exist.
				handler = getattr(ext, signal, None)
				if handler: signals[signal].append(handler)
			
			if hasattr(ext, '__call__'):  # This one is aliased; the extension itself is treated as WSGI middleware.
				signals['middleware'].append(ext)
		
		# Certain operations act as a stack, i.e. "before" are executed in dependency order, but "after" are executed
		# in reverse dependency order.  This is also the case with "mutate" (incoming) and "transform" (outgoing).
		for signal in inverse:
			signals[signal].reverse()
		
		# Transform the signal lists into tuples to compact them.
		self.signal = Context(**{k: tuple(v) for k, v in items(signals)})
		
		# This will save a chain() call on each request by pre-prepending the two lists.
		# Attempts to add extensions during runtime are complicated by this optimization.
		self.signal['pre'] = tuple(signals['prepare'] + signals['before'])
		
		# Continue up the chain with the `ExtensionManager` initializer, using the `web.extension` namespace.
		super(WebExtensions, self).__init__('web.extension')

