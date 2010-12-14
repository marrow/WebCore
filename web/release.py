# encoding: utf-8

"""Release information about WebCore."""

import sys


__all__ = ['name', 'version', 'version_info', 'release', 'summary', 'description', 'author', 'email', 'url', 'download_url', 'copyright', 'license', 'colophon']



name = "WebCore"
version = "1.0.1"
version_info = (1, 0, 1, 'production', 0)
release = "1.0"

summary = "A full-stack, light-weight and efficient web development framework."
description = """"""
author = "Alice Bevan-McGregor"
email = "alice@gothcandy.com"
url = "http://www.web-core.org/"
download_url = "http://cheeseshop.python.org/pypi/WebCore/"
copyright = "2009-2010, Alice Bevan-McGregor and contributors"
license = "MIT"
colophon = """Powered by <a class="noicon" href="http://www.python.org/" title="A programming language that lets you work more quickly and integrate your systems more effectively.">Python</a> <em class="version">""" + "%d.%d" % sys.version_info[:2] + """</em> and <a class="noicon" href="http://www.web-core.org/" title="A lightweight and extremely fast Python web framework.">WebCore</a> <em class="version">""" + release + "</em>."
