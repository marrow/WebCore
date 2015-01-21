# encoding: utf-8

from __future__ import unicode_literals

from marrow.package.lookup import traverse


def always(context):
	return True


def never(context):
	return False


def anonymous(context):
	"""Grant access if the user is anonymous."""
	
	return (web.auth.user is None) or None


def authenticated(context):
	"""Grant access if the user is authenticated."""
	
	return (web.auth.user is not None) or None


def attribute(attr, values=[], target='user'):
	"""Grant access if an attribute of the user or another object from the context, is present in a list of values."""
	
	def attribute_check(context):
		return (traverse(context, target + '.' + attr, None) in values) or None
	
	return attribute_check


def value(attr, value, target='user'):
	"""Grant access if a value is present in an attribute of the user, or other, object from the context."""
	
	def value_check(context):
		return (value in traverse(context, target + '.' + attr, [])) or None
	
	return value_check
