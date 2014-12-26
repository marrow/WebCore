# encoding: utf-8

from __future__ import unicode_literals, print_function

from web.core.compat import py3

try:
	from marrow.schema import Container, Attribute
except ImportError:  # pragma: no-cover
	print("Unable to find the marrow.schema package. To correct this, run: pip install marrow.schema")
	raise


class Rule(Container):
	"""The basic data structure and abstract API for ACL rules.
	
	ACL rules evaluate to `None` (doesn't apply), `False` (deny access), or `True` (allow access).
	
	Used by itself this rule represents an always grant or always fail.
	"""
	
	__slots__ = ('__data__', )
	
	grant = Attribute(default=False)  # Be a little paranoid; deny access by default.
	inverse = Attribute(default=False)  # Pass or fail if the rule does not match.
	
	def __call__(self, context):
		"""Override this in subclasses; use the super() call after determining if your rule applies."""
		
		return not self.grant if self.inverse else self.grant
	
	def __repr__(self):
		"""The default programmers' representation is generic."""
		
		return "{0}({1})".format(self.__class__.__name__, self)
	
	def __unicode__(self):
		"""This representation is useful to super() call into."""
		
		return '{0} {1}'.format(
				'grant' if self.grant else 'deny',
				'if not' if self.inverse else 'if',
			)
	
	if py3:  # pragma: no cover
		__str__ = __unicode__
		del __unicode__
