# encoding: utf-8

"""Compatibility helpers to bridge the differences between Python 2 and Python 3.

Similar in purpose to [`six`](https://warehouse.python.org/project/six/).
"""

# ## Imports

import sys
import json


# ## Version Detection

py2 = sys.version_info < (3, )
py3 = sys.version_info > (3, )
pypy = hasattr(sys, 'pypy_version_info')


# ## Builtins Compatibility

if py3:
	native = str
	unicode = str
	str = bytes
	basestring = unicode
	keys = dict.keys
	values = dict.values
	items = dict.items
	zip = zip
else:
	native = str
	unicode = unicode
	str = str
	basestring = (str, unicode)
	range = xrange
	keys = dict.iterkeys
	values = dict.itervalues
	items = dict.iteritems
	from itertools import izip as zip

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

