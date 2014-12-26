# encoding: utf-8

"""Compatibility helpers to bridge the differences between Python 2 and Python 3.

Similar in purpose to [`six`](https://warehouse.python.org/project/six/).
"""

# ## Imports

import sys


# ## Version Detection

py2 = sys.version_info < (3, )
py3 = sys.version_info > (3, )
pypy = hasattr(sys, 'pypy_version_info')


# ## Builtins Compatibility

if py3:  # pragma: no cover
	native = str
	unicode = str
	str = bytes
	iterkeys = dict.keys
	itervalues = dict.values
	iteritems = dict.items
else:  # pragma: no cover
	native = str
	unicode = unicode
	str = str
	range = xrange
	iterkeys = dict.iterkeys
	itervalues = dict.itervalues
	iteritems = dict.iteritems


# ## Ordered Dictionaries

try:  # pragma: no cover
	from collections import OrderedDict as odict
except ImportError:  # pragma: no cover
	from ordereddict import OrderedDict as odict


# ## File-Like String Handling

try:  # pragma: no cover
	try:  # pragma: no cover
		from cStringIO import StringIO
	except ImportError:  # pragma: no cover
		from StringIO import StringIO
except ImportError:  # pragma: no cover
	from io import StringIO
