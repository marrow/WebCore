# encoding: utf-8

"""Compatibility helpers to bridge the differences between Python 2 and Python 3.

Similar in purpose to [`six`](https://warehouse.python.org/project/six/).
"""

# ## Imports

import sys


# ## Version Detection

py3 = sys.version_info > (3, )
pypy = hasattr(sys, 'pypy_version_info')


# ## Builtins Compatibility

if py3:
	unicode = str
	str = bytes
	basestring = unicode
	items = dict.items
else:
	unicode = unicode
	str = str
	basestring = (str, unicode)
	range = xrange
	items = dict.iteritems

# ## Ordered Dictionaries

try:
	from collections import OrderedDict as odict
except ImportError:
	from ordereddict import OrderedDict as odict


# ## File-Like String Handling

try:
	try:
		from cStringIO import StringIO
	except ImportError:
		from StringIO import StringIO
except ImportError:
	from io import StringIO

