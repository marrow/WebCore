# encoding: utf-8
# pragma: no cover

import warnings

from marrow.util.object import yield_property, CounterMeta
from marrow.util.object import load_object as get_dotted_object


__all__ = ['yield_property', 'CounterMeta', 'get_dotted_object']


warnings.warn("Use of the web.utils.object module is deprecated; use marrow.util.object instead.")
