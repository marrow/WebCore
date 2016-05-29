# encoding: utf-8

"""Database connection handling extension."""

from functools import partial

from ..core.context import ContextGroup


class DBExtension(object):
	__slots__ = ('engines', )
	
	provides = {'db'}
	
	def __init__(self, default=None, **engines):
		engines['default'] = default
		self.engines = engines
		
		self.uses = set()
		self.needs = set()
		self.provides = set(self.provides)
		
		for name, engine in engines.items():
			if engine is None: continue
			engine.__name__ = name  # Inform the engine what its name is.
			self.uses.update(getattr(engine, 'uses', ()))
			self.needs.update(getattr(engine, 'needs', ()))
			self.provides.update(getattr(handler, 'provides', ()))
		
		super().__init__()
	
	def start(self, context):
		context._DB = type('DBGroup', (ContextGroup, ), dict(self.engines))
		self._handle_event('start', context)
	
	def prepare(self, context):
		context.db = context._DB(_ctx=context)
		self._handle_event('prepare', context)
	
	def _handle_event(self, event, *args, **kw):
		for handler in self.handlers.values():
			if handler is not None and hasattr(handler, event):
				getattr(handler, event)(*args, **kw)
	
	def __getattr__(self, name):
		if name not in ('stop', 'graceful', 'dispatch', 'before', 'after', 'done', 'interactive', 'inspect'):
			raise AttributeError()
		
		return partial(self._handle_event, name)

