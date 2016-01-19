# encoding: utf-8

from __future__ import unicode_literals

from marrow.package.host import ExtensionManager

from .context import Context


log = __import__('logging').getLogger(__name__)


class WebExtensions(ExtensionManager):
	SIGNALS = (  # Extension hooks.
			'start',  # Executed during Application construction.
			'stop',  # Executed when (and if) the serve() server returns.
			'graceful',  # Executed when (and if) the process is instructed to reload configuration.
			'prepare',  # Executed during initial request processing.
			'dispatch',  # Executed once for each dispatch event.
			'before',  # Executed after all extension `prepare` methods have been called, prior to dispatch.
			'after',  # Executed after dispatch has returned and the response populated.
			'mutate',  # Inspect and potentially mutate arguments to the handler prior to execution.
			'transform',  # Transform the result returned by the handler and apply it to the response.
			'middleware',  # Executed to allow WSGI middleware wrapping.
		)
	
	def __init__(self, ctx):
		# TODO: Do a touch more than this, such as named plugin loading / configuration unpacking for dict/yaml-
		# based loading.
		self.feature = set()
		self.all = self.order(ctx.app.config)
		signals = {signal: [] for signal in self.SIGNALS}
		
		for ext in self.all:
			self.feature.update(getattr(ext, 'provides', []))
			
			for mn in self.SIGNALS:
				m = getattr(ext, mn, None)
				if m: signals[mn].append(m)
			
			if hasattr(ext, '__call__'):  # This one is aliased; the extension itself is treated as WSGI middleware.
				signals['middleware'].append(ext)
		
		# Certain operations act as a stack, i.e. "before" are executed in dependency order, but "after" are executed
		# in reverse dependency order.  This is also the case with "mutate" (incoming) and "transform" (outgoing).
		signals['after'].reverse()
		signals['transform'].reverse()
		signals['middleware'].reverse()
		
		self.signal = Context(**{k: tuple(v) for k, v in signals.items()})  # Packaged up, ready to go.
		self.signal['pre'] = tuple(signals['prepare'] + signals['before'])  # Save a chain() on each request.
		
		super(WebExtensions, self).__init__('web.extension')
