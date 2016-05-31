# encoding: utf-8

"""Database connection handling extension."""

from functools import partial

from ..core.context import ContextGroup


class DBExtension(object):
	__slots__ = ('engines', 'uses', 'needs', 'provides')
	
	_provides = {'db'}
	
	def __init__(self, default=None, **engines):
		engines['default'] = default
		self.engines = engines
		
		self.uses = set()
		self.needs = set()
		self.provides = set(self._provides)
		
		for name, engine in engines.items():
			if engine is None: continue
			engine.__name__ = name  # Inform the engine what its name is.
			self.uses.update(getattr(engine, 'uses', ()))
			self.needs.update(getattr(engine, 'needs', ()))
			self.provides.update(getattr(engine, 'provides', ()))
		
		super().__init__()
	
	def start(self, context):
		context.db = ContextGroup(**self.engines)
		self._handle_event('start', context)
	
	def prepare(self, context):
		context.db = context.db._promote('DBGroup')
		context.db['_ctx'] = context
		
		self._handle_event('prepare', context)
	
	def _handle_event(self, event, *args, **kw):
		for engine in self.engines.values():
			if engine is not None and hasattr(engine, event):
				getattr(engine, event)(*args, **kw)
	
	def __getattr__(self, name):
		if name not in ('stop', 'graceful', 'dispatch', 'before', 'after', 'done', 'interactive', 'inspect'):
			raise AttributeError()
		
		return partial(self._handle_event, name)

