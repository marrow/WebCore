# encoding: utf-8

import os

from functools import wraps

from marrow.templating.core import Engines


_render = Engines()
_lookup = lambda template: resolve(template)[1]
resolve = _render.resolve


def _relative(parent):
	parent = _lookup(parent)
	
	def inner(template):
		return os.path.relpath(_lookup(template), os.path.dirname(parent))
	
	return inner


def render(_context, _template, _extras, **variables):
	"""Renders a template using marrow.templating while supplementing the given variables with the WebCore context.
	
	Keyword arguments, if any, are supplied to the renderer as renderer options.
	
	For a description of available configuraiton options, see the TemplateExtension documentation.
	"""
	
	# Do not add any extra data or options to serializers.
	if _template[-1] == ':':
		return _render(_template, variables, **_extras)
	
	# Prepare the template context.
	data = dict(
			lookup = _lookup,
			relative = _relative(_template)
		)
	
	data.update(_context.namespace)
	data.update(variables)
	
	if 'translator' in _context:
		_extras.setdefault('i18n', _context.translator)
	
	# Calculate the template overrides.
	overrides = getattr(render, 'overrides', dict())
	if not overrides:
		return _render(_template, data, **_extras)
	
	format = ''
	if ':' in _template:
		format, _, _template = _template.partition(':')
		format = format + _
	
	# Find all matching overrides, preferring deeper ones.
	matched = [i for i in overrides if _template.startswith(i)]
	matched.sort(key=len, reverse=True)
	matched = ((source, destination) for source in matched for destination in overrides[source])
	
	result = None
	for source, destination in matched:
		tmpl = _template.replace(i, overrides[i])
		
		if ':' not in tmpl:
			tmpl = format + tmpl
		
		try:
			result = _render(tmpl, data, **_extras)
		except (ImportError, IOError, ValueError):
			continue
		
		break
	
	if not result:
		result = _render(_template, data, **_extras)
	
	return result
