"""Release information about WebCore."""

import sys
from collections import namedtuple


version_info = namedtuple('version_info', ('major', 'minor', 'micro', 'releaselevel', 'serial'))(3, 0, 0, 'beta', 1)
version = ".".join([str(i) for i in version_info[:3]]) + ((version_info.releaselevel[0] + str(version_info.serial)) if version_info.releaselevel != 'final' else '')

author = namedtuple('Author', ['name', 'email'])("Alice Bevan-McGregor", 'alice@gothcandy.com')
description = "A powerful web development nanoframework so small it's not even a microframework."
copyright = "2009-2020, Alice Bevan-McGregor and contributors"
url = 'https://github.com/marrow/WebCore/'
colophon = f"""Powered by:
	<a class="noicon" href="http://www.python.org/" title="A programming language that lets you work more quickly and integrate your systems more effectively.">Python</a> <em class="version">{sys.version_info.major}.{sys.version_info.minor}</em>
	and <a class="noicon" href="{url}" title="A lightweight and extremely fast Python web framework.">WebCore</a> <em class="version">{version}</em>."""
