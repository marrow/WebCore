# encoding: utf-8

"""Release information about WebCore."""

import sys
from collections import namedtuple


__all__ = ['version_info', 'version', 'copyright', 'colophon']


version_info = namedtuple('version_info', ('major', 'minor', 'micro', 'releaselevel', 'serial'))(1, 1, 2, 'final', 0)

version = ".".join([str(i) for i in version_info[:3]]) + ((version_info.releaselevel[0] + str(version_info.serial)) if version_info.releaselevel != 'final' else '')

copyright = "2009-2011, Alice Bevan-McGregor and contributors"
colophon = """Powered by <a class="noicon" href="http://www.python.org/" title="A programming language that lets you work more quickly and integrate your systems more effectively.">Python</a> <em class="version">""" + "%d.%d" % sys.version_info[:2] + """</em> and <a class="noicon" href="http://www.web-core.org/" title="A lightweight and extremely fast Python web framework.">WebCore</a> <em class="version">""" + version + "</em>."
