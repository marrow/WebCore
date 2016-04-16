=======
WebCore
=======

    © 2006-2016 Alice Bevan-McGregor and contributors.

..

    https://github.com/marrow/WebCore

..

    |latestversion| |downloads| |masterstatus| |mastercover| |issuecount|



Installation
============

Installing ``WebCore`` is easy, just execute the following in a terminal::

    pip install WebCore

**Note:** We *strongly* recommend always using a container, virtualization, or sandboxing environment of some kind when
developing using Python; installing things system-wide is yucky (for a variety of reasons) nine times out of ten.  We
prefer light-weight `virtualenv <https://virtualenv.pypa.io/en/latest/virtualenv.html>`_, others prefer solutions as
robust as `Vagrant <http://www.vagrantup.com>`_.

If you add ``WebCore`` to the ``install_requires`` argument of the call to ``setup()`` in your application's
``setup.py`` file, WebCore will be automatically installed and made available when your own application or
library is installed.  We recommend using "less than" version numbers to ensure there are no unintentional
side-effects when updating.  Use ``WebCore<2.1`` to get all bugfixes for the current release, and
``WebCore<3.0`` to get bugfixes and feature updates while ensuring that large breaking changes are not installed.

Dependencies and Extras
-----------------------

WebCore only depends on the excellent `webob <http://webob.org>`_ package to provide request, response, and HTTP
status code exception helpers. All other dependencies will be application dependencies; choice of template engine,
database layer, session storage mechanism, and even dispatch method are left entirely up to the developer making use
of the framework. Provided are a number of ``extras`` requirements, which you can define using a comma-separated list
appended to the package name during installation from the command-line, or within your own package's
``install_requires``.

The available extras are:

- ``development`` -- this installs a recommended set of development-time packages, including
  `pytest <http://pytest.org/>`_ and a suite of plugins for it, plus the 
  `backlash <https://github.com/TurboGears/backlash>`_ interactive debugger (needed by the optional
  ``DebugExtension``), object dispatch, the comprehensive ``ptipython`` upgraded REPL, and the
  `waitress <https://github.com/Pylons/waitress>`_ development web server.

- ``production`` -- install recommended production-time packages; currently this only installs the ``flup`` FastCGI
  server bridge.

The default choices for disatch are allowed as extras:

- ``object`` -- install object dispatch

- ``route`` -- install route-based dispatch

- ``traversal`` -- install traversal dispatch

You can also name a supported server bridge as an extra.  Currently available bridges with third-party dependencies include:

- ``waitress``

- ``tornado``

- ``flup``

Development Version
-------------------

    |developstatus| |developcover|

Development takes place on `GitHub <https://github.com/>`_ in the
`WebCore <https://github.com/marrow/WebCore/>`_ project.  Issue tracking, documentation, and downloads
are provided there.

Installing the current development version requires `Git <http://git-scm.com/>`_, a distributed source code management
system.  If you have Git you can run the following to download and *link* the development version into your Python
runtime::

    git clone https://github.com/marrow/WebCore.git
    pip install -e WebCore

You can then upgrade to the latest version at any time::

    (cd cinje; git pull; pip install -e .)

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes,
and submit a pull request.  This process is beyond the scope of this documentation; for more information see
`GitHub's documentation <http://help.github.com/>`_.


Version History
===============

Version 2.0
-----------

* Modern rewrite for ultimate minamalism and Python 2 & 3 + Pypy cross-support.


License
=======

WebCore has been released under the MIT Open Source license.

The MIT License
---------------

Copyright © 2006-2016 Alice Bevan-McGregor and contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


.. |masterstatus| image:: http://img.shields.io/travis/marrow/WebCore/master.svg?style=flat
    :target: https://travis-ci.org/marrow/WebCore
    :alt: Release Build Status

.. |developstatus| image:: http://img.shields.io/travis/marrow/WebCore/develop.svg?style=flat
    :target: https://travis-ci.org/marrow/WebCore
    :alt: Development Build Status

.. |latestversion| image:: http://img.shields.io/pypi/v/WebCore.svg?style=flat
    :target: https://pypi.python.org/pypi/WebCore
    :alt: Latest Version

.. |downloads| image:: http://img.shields.io/pypi/dw/WebCore.svg?style=flat
    :target: https://pypi.python.org/pypi/WebCore
    :alt: Downloads per Week

.. |mastercover| image:: http://img.shields.io/codecov/c/github/marrow/WebCore/master.svg?style=flat
    :target: https://codecov.io/github/marrow/WebCore?branch=master
    :alt: Release Test Coverage

.. |developcover| image:: http://img.shields.io/codecov/c/github/marrow/WebCore/develop.svg?style=flat
    :target: https://codecov.io/github/marrow/WebCore?branch=develop
    :alt: Development Test Coverage

.. |issuecount| image:: http://img.shields.io/github/issues/marrow/WebCore.svg?style=flat
    :target: https://github.com/marrow/WebCore/issues
    :alt: Github Issues

.. |cake| image:: http://img.shields.io/badge/cake-lie-1b87fb.svg?style=flat

