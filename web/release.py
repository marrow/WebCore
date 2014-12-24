# encoding: utf-8

"""Release information about WebCore."""

from __future__ import unicode_literals

import sys
from collections import namedtuple


version_info = namedtuple('version_info', ('major', 'minor', 'micro', 'releaselevel', 'serial'))(2, 0, 0, 'alpha', 1)
version = ".".join([str(i) for i in version_info[:3]]) + ((version_info.releaselevel[0] + str(version_info.serial)) if version_info.releaselevel != 'final' else '')

author = namedtuple('Author', ['name', 'email'])("Alice Bevan-McGregor", 'alice@gothcandy.com')
description = "A full-stack, light-weight and efficient web development framework."
copyright = "2009-2014, Alice Bevan-McGregor and contributors"
url = 'http://web-core.org/'
colophon = """Powered by:
	<a class="noicon" href="http://www.python.org/" title="A programming language that lets you work more quickly and integrate your systems more effectively.">Python</a> <em class="version">{0.major}.{0.minor}</em>
	and <a class="noicon" href="{1}" title="A lightweight and extremely fast Python web framework.">WebCore</a> <em class="version">{2}</em>.""".format(sys.version_info, url, version)
