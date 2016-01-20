# encoding: utf-8

from __future__ import unicode_literals

from weakref import ref
from inspect import isclass
from marrow.package.host import PluginManager


log = __import__('logging').getLogger(__name__)


class WebDispatchers(PluginManager):
	__isabstractmethod__ = False
	
	def __init__(self, ctx):
		self._ctx = ref(ctx)  # Stored for later use during dispatcher configuration.
		# The above is a weak reference to try to reduce cycles; a WebDispatchers instance is itself stored in the context.
		
		super(WebDispatchers, self).__init__('web.dispatch')
	
	def __getitem__(self, name):
		if hasattr(name, '__call__'):
			return name
		
		# If the dispatcher isn't already executable, it's probably an entry point reference. Load it from cache.
		dispatcher = super(WebDispatchers, self).__getitem__(name)
		
		# If it's uninstantiated, instantiate it.
		if isclass(dispatcher):
			# TODO: Extract **kw settings from context.
			dispatcher = self.named[name] = dispatcher()  # Instantiate and update the entry point cache.
		
		if __debug__:
			log.debug("Loaded dispatcher.", extra=dict(dispatcher=repr(dispatcher)))
		
		return dispatcher
