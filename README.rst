=======
WebCore
=======

    © 2006-2020 Alice Bevan-McGregor and contributors.

..

    https://github.com/marrow/WebCore

..

    |latestversion| |ghtag| |downloads| |masterstatus| |mastercover| |masterreq| |ghwatch| |ghstar|


1. `What is WebCore?`_

2. `Installation`_

   1. `Dependencies and Extras`_

   2. `Development Version`_

3. `Basic Concepts`_

   1. `Application`_

   2. `Context`_

   3. `Controllers, Endpoints, Dispatch, Oh My!`_

4. `Plugins and Namespaces`_

5. `Version History`_

6. `License`_


What is WebCore?
================

WebCore is a nanoframework, a fraction of the size of competing "microframeworks", and culmination of more than ten
years of web development experience. It provides a clean API for standard points of extension while strongly
encouraging model, view, controller separation. Being less than 400 source lines of code (SLoC; excluding comments and
documentation) and containing more comments and lines of documentation than lines of code, WebCore is built to be
insanely easy to test, adapt, and use, allowing any developer familiar with programming (not just Python programming)
to be able to read and understand the entirety of the framework in an evening.

It is substantially smaller and more efficient than monolithic frameworks such as Django or Pyramid::

    from web.core import Application
    
    Application("Hi.").serve('wsgiref')

Really; that's it. (It can be made into one line if you're willing to make the import ugly using ``__import__``.) The
Application class represents a standard Python WSGI application, the rest is up to you to pick the components that
best fit your own needs.


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
status code exception helpers and the `marrow.package <https://github.com/marrow/package>`_ utility package for plugin
management. All other dependencies will be application dependencies; choice of template engine,
database layer, session storage mechanism, and even dispatch method are left entirely up to the developer making use
of the framework. Provided are a number of ``extras`` requirements, which you can define using a comma-separated list
appended to the package name during installation from the command-line, or within your own package's
``install_requires``. For example, to install a typical set of development tools at the same time as WebCore, run::

    pip install WebCore[development]

The available extras are:

- ``development`` -- this installs a recommended set of development-time packages, including
  `pytest <http://pytest.org/>`_ and a suite of plugins for it, plus the 
  `backlash <https://github.com/TurboGears/backlash>`_ interactive debugger (needed by the optional
  ``DebugExtension``), object dispatch, the comprehensive ``ptipython`` upgraded REPL, and the
  `waitress <https://github.com/Pylons/waitress>`_ development web server.

- ``production`` -- install recommended production-time packages; currently this only installs the ``flup`` FastCGI
  server bridge.

The default choices for dispatch are allowed as extras:

- ``object`` -- install object dispatch

- ``route`` -- install route-based dispatch

- ``traversal`` -- install traversal dispatch

You can also name a supported server bridge as an extra.  Currently available bridges with third-party dependencies include:

- ``waitress``

- ``tornado``

- ``flup``

Development Version
-------------------

|developstatus| |developcover| |ghsince| |issuecount| |ghfork|

Development takes place on `GitHub <https://github.com/>`_ in the
`WebCore <https://github.com/marrow/WebCore/>`_ project.  Issue tracking, documentation, and downloads
are provided there. Development chat (both development of WebCore and chat for users using WebCore to develop their
own solutions) is graciously provided by `Freenode <ircs://chat.freenode.net:6697/#webcore>`_ in the ``#webcore``
channel.

Installing the current development version requires `Git <http://git-scm.com/>`_, a distributed source code management
system.  If you have Git you can run the following to download and *link* the development version into your Python
runtime::

    git clone https://github.com/marrow/WebCore.git
    pip install -e WebCore

You can then upgrade to the latest version at any time::

    (cd WebCore; git pull; pip install -e .)

Extra dependenies can be declared the same as per web-based installation::

    pip install -e WebCore[development]

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes,
and submit a pull request.  This process is beyond the scope of this documentation; for more information see
`GitHub's documentation <http://help.github.com/>`_.


Basic Concepts
==============

Application
-----------

The ``Application`` class is the primary entry point for the web framework. Its constructor currently takes up to
three arguments:

- ``root`` -- the root object to use as the controller for ``/`` requests

- ``extensions`` -- a list of extensions to use with your application

- ``logging`` -- Python ``logging`` configuration

The "root controller" is used as the starting point for dispatch resolution of the endpoint for a request, see the
Controllers section below for details on what can be used here, but it's basically anything.

By defualt the ``BaseExtension``, providing basic request and response objects and baisc views, is always enabled for 
your application, has no configuration, and does not need to be instantiated yourself. Other extensions should be
instantiated and passed in the ``extensions`` list.

Logging configuration offers two choices: simple "global logging level" by defining ``logging`` as a dictionary
only containing a ``level`` key naming the level to set, or full ``logging.config.dictConfig`` configuration. Passing
only a level is equivalent to running ``logging.basicConfig``.

This configuration can entirely come from YAML, for example::

    root: !!python/name:web.app.example.RootController
    
    extensions:
        - !!python/object:web.ext.debug.DebugExtension
        - !!python/object:web.ext.analytics.AnalyticsExtension
        - !!python/object:web.ext.annotation:AnnotationExtension
    
    logging:
        level: debug

This would make managing complex extension configuration easier. One way to invoke WebCore with a configuration like
this, while allowing for a distinction between production and development environments and use under ModWSGI would
be::

    import yaml
    from web.core import Application
    
    fname = 'development.yaml' if __debug__ else 'production.yaml'
    with open(fname, 'r', encoding='utf-8') as fh:
        config = yaml.load(fh)
    
    app = Application(**config)
    
    if __name__ == "__main__":
        app.serve('wsgiref')

Now, running ``python run.py`` (if saved as ``run.py``) would serve the ``development.yaml`` configuration, and
running as ``python -O run.py`` (optimization enabled) or with ``PYTHONOPTIMIZE=1`` set in the environment will
utilize the ``production.yaml`` file.

WebCore is highly aware running with optimizations enabled, eliminating many of the expensive validation checks that
are only really useful in development. For example, calling an endpoint with invalid arguments will ``404`` with a
friendly warning in development, but ``500`` in production as the ``TypeError`` is not preemptively checked and
caught; this is one of the most expensive validation checks. Feel free to browse the code looking for ``if __debug__``
blocks to see what else changes in "production mode".

The order you define the extensions in does not matter; they declare dependencies and will be automatically
dependency-ordered when collecting callbacks. Please see the ``extension.py`` example for additional information on
what you can do with them.


Context
-------

The overall application has an ``ApplicationContext`` associated with it. This object is passed around to the various
extension callbacks and acts as an attribute access dictionary.  (All of the typical dictionary methods will work,
and the keys can be accessed as attributes instead, saving some typing.) During the processing of a request a subclass
is constructed called ``RequestContext`` and in-request extension callbacks, and your controller endpoints, are given
a reference to this instance.

The attributes present in the base ``ApplicationContext`` are:

- ``app`` -- a reference to the ``Application`` instance

- ``root`` -- the original object passed when constructing the ``Application`` instance

- ``extension`` -- the ``WebExtensions`` extension registry

- ``dispatch`` -- the ``WebDispatchers`` dispatch protocol bridge and plugin registry

- ``view`` -- the ``WebViews`` view handler registry

Extensions would access these during ``start`` and ``stop`` events, for example to register new view handlers.

The attributes present in the ``RequestContext`` (added by WebCore itself or the ``BaseExtension`` during request
processing) are:

- ``environ`` -- the WSGI request environment as passed to WebCore's WSGI handler

- ``request`` -- a ``webob.Request`` representing the current HTTP request

- ``response`` -- a ``webob.Response`` object corresponding to the response WebCore will return

- ``path`` -- a list of dispatch steps represented by tuples of ``(handler, script_name)``

Additional attributes may be added by other extensions.


Controllers, Endpoints, Dispatch, Oh My!
----------------------------------------

Controllers and, more generally, *callable endpoints*, are functions or methods called to process a request and return
a value for view or raise an exception. Non-method callables are passed the context as a first argument; methods are
assumed to have access via ``self`` as the context will have been passed as the only positional argument to the class
constructor. *Callable endpoints* are additionally passed any unprocessed path elements as positional parameters, and
a combination of query string arguments (``GET`` values) and form-encoded body elements (``POST`` values) as keyword
arguments, with arguments from the request body taking precedence and duplicated keys being passed as a list of
values. They may return any value there is a view registered for, see the
`docstring of the view manager <https://github.com/marrow/WebCore/blob/develop/web/core/view.py?ts=4>`_ for details.

*Static endpoints*, on the other hand, are non-callable objects that can be handled by a view. The very first example
at the top of this document relies on the fact that there is a view to handle strings, both static, and as returned by
a *callable endpoint* such as::

    def hello(context):
        return "Hello world!"

To allow for customization of the name, you would write this endpoint as::

    def hello(context, name="world"):
        return "Hello {}!".format(name)

As noted in the Application section, when Python is run with optimizations enabled (``-O`` or ``PYTHONOPTIMIZE`` set)
unknown arguments being passed (unknown query string arguments or form values) will result in a ``TypeError`` being
raised and thus a ``500 Internal Server Error`` due to the uncaught exception. In development (without optimizations)
a ``404 Not Found`` error with a message indicating the mismatched values will be the result. You can use ``*args``
and ``**kwargs`` to capture any otherwise undefined positional and keyword arguments, or use an extension to mutate
the incoming data and strip invalid arguments prior to the endpoint being called.

That "hello world" endpoint, however, may be called in one of several different ways, as no other restrictions have
been put in place:

- ``GET /`` -- Hello world! (Default used.)

- ``GET /Alice`` -- Hello Alice! (Passed positionally.)

- ``GET /?name=Bob`` -- Hello Bob! (Via query string assignment.)

- ``POST /`` submitting a form with a ``name`` field and value of ``Eve`` -- Hello Eve! (Via form-encoded body
  assignment.)

Other HTTP verbs will work as well, but a form-encoded body is only expected and processed on ``POST`` requests.

The process of finding the endpoint to use to process a request is called *dispatch*. There are a number of forms of
dispatch available, some should be immediately familiar.

- **Object dispatch.** This is the default (providided by the 
  `web.dispatch.object <https://github.com/marrow/web.dispatch.object>`_ package) form of dispatch for WebCore, and
  is also utilized by several other frameworks such as TurboGears. Essentially each path element is looked up as
  an attribute of the previously looked up object treating a path such as ``/foo/bar/baz`` as an attempt to resolve
  the Python reference ``root.foo.bar.baz``. This is quite flexible, allowing easy redirection of descent using
  Python-standard protocols such as ``__getattr__`` methods, use of lazy evaluation descriptors, etc., etc.

- **Registered routes.** This will likely be the approach most familiar to developers switching from PHP frameworks or
  who have used any of the major macro- or micro-frameworks in Python such as Django, Flask, etc. You explicitly map 
  URLs, generally using a regular expression or regular expression short-hand, to specific callable endpoints. Often
  this is a accomplished using a decorator. WebCore offers this form of dispatch throuhg the
  `web.dispatch.route <https://github.com/marrow/web.dispatch.route>`_ package.

- **Traversal.** This is similar to object dispatch, but descending through mapping keys. The previous example then
  translates to ``root['foo']['bar']['baz']``, allowing managed descent through the ``__getitem__`` protocol. This
  is one of the methods (the other being routes) provided by Pyramid. We offer this form of dispatch through the
  `web.dispatch.traversal <https://github.com/marrow/web.dispatch.traversal>`_ package.

There may be other dispatchers available and the protocol allows for "dispatch middleware" to offer even more flexible
approaches to endpoint lookup. The dispatch protocol itself is framework agnostic (these example dispatchers are in
no way WebCore-specific) and
`has its own documentation <https://github.com/marrow/protocols/blob/master/dispatch/README.md>`_.


Plugins and Namespaces
======================

WebCore recommends registration of extensions and other plugins as Python-standard ``entry_points`` references.
Please see the `relevant setuptools documentation 
<https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins>`_ for details on this
process. Additionally, WebCore marks package namespaces for shared use. The namespaces used, and their purposes, are:

- ``web`` -- the top level shared namespace for WebCore and WebCore accessories

- ``web.app`` -- a namespace for reusable application components and your own use

- ``web.ext`` -- a namespace for WebCore extensions; your own can be placed here

- ``web.server`` -- light-weight WSGI server adapters; your own WSGI server can define a dependency-free adapter
  here, for example

The plugin namespaces follow a similar pattern:

- ``web.app`` -- re-usable components you can attach to your own controller trees

- ``web.extension`` -- extensions registered by name and "provides" tag

- ``web.server`` -- similarly, server adapters registered by name

WebCore also makes use of the ``web.dispatch`` namespace to look up dispatchers. Other WebCore-related packages and
extensions may make use of other plugin namespaces. Have a gander at WebCore's ``setup.py`` file for an example of
how to register plugins this way, and copy the ``__init__.py`` file from the ``web`` package into the overlay in your
own package (and declare such in your ``setup.py`` package metadata as the ``namespace_packages`` argument) to
participate in the Python package namespaces.


Version History
===============

Version 2.0
-----------

- A complete modernization rewrite of WebCore, from the ground up.
- Features multiple extension interfaces to extend registered view handlers and provide a uniform callback mechanism.
- Standard usage makes use of no superglobals or "thread locals", instead relying on a context object collaboratively
  populated by extensions.
- WebCore's former "dialect" system is now dispatch.

Version 2.0.1
-------------

- Thanks Pypi.

Version 2.0.2
-------------

- Corrected argument specification for ``transform`` extension callbacks, fixing ``AnnotationExtension`` usage as per
  `#163 <https://github.com/marrow/WebCore/issues/163>`_.
- Additional source-level documentation and expanded examples.
- An excessively large number of additional WSGI server adapters; now supported are: waitress
  `tornado <http://s.webcore.io/aIaN>`_, `fcgi <http://s.webcore.io/fhVY>`_,
  `cherrypy <http://s.webcore.io/aIoF>`_, `appengine <http://s.webcore.io/aIic>`_, `paste <http://s.webcore.io/aIdT>`_,
  `eventlet <http://s.webcore.io/aIaa>`_, `gevent <http://s.webcore.io/aIpU>`_, `diesel <http://s.webcore.io/aIg2>`_,
  and `bjoern <http://s.webcore.io/aIne>`_. Each is available as an ``extras_require`` by the same name which will
  pull in the required third-party dependency.

Version 2.0.3
-------------

- Argument processing moved out of ``web.core`` into extension ``mutate`` handlers. Features improved rich
  unflattening of query string and form encoded body parameters.  Configurable behaviour. For details, see:
  `web/ext/args.py <https://github.com/marrow/WebCore/blob/develop/web/ext/args.py>`_
- `Extensively documented <https://github.com/marrow/WebCore/blob/develop/web/ext/acl.py>`_ access control list
  extension validating endpoint security and return value permission using context-aware predicates.
- The ability for extensions to define additional callbacks for collection.
- The ``DatabaseExtension`` (formerly ``DBExtension``) has been moved into `its own repository
  <https://github.com/marrow/web.db>`_.
- Content negotiation endpoint return value serialization, with pluggable ``dumps`` registry.
- Complete unit test coverage.

Version 2.0.4
-------------

- Correction for a failure to elide trailing slashes in the base extension processing of dispatch events.
  Resulted in an erroneous empty string positional argument via unmatched path processing. `#195
  <https://github.com/marrow/WebCore/issues/195>`_


License
=======

WebCore has been released under the MIT Open Source license.

The MIT License
---------------

Copyright © 2006-2020 Alice Bevan-McGregor and contributors.

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



.. |ghwatch| image:: https://img.shields.io/github/watchers/marrow/WebCore.svg?style=social&label=Watch
    :target: https://github.com/marrow/WebCore/subscription
    :alt: Subscribe to project activity on Github.

.. |ghstar| image:: https://img.shields.io/github/stars/marrow/WebCore.svg?style=social&label=Star
    :target: https://github.com/marrow/WebCore/subscription
    :alt: Star this project on Github.

.. |ghfork| image:: https://img.shields.io/github/forks/marrow/WebCore.svg?style=social&label=Fork
    :target: https://github.com/marrow/WebCore/fork
    :alt: Fork this project on Github.

.. |masterstatus| image:: http://img.shields.io/travis/marrow/WebCore/master.svg?style=flat
    :target: https://travis-ci.org/marrow/WebCore/branches
    :alt: Release build status.

.. |mastercover| image:: http://img.shields.io/codecov/c/github/marrow/WebCore/master.svg?style=flat
    :target: https://codecov.io/github/marrow/WebCore?branch=master
    :alt: Release test coverage.

.. |masterreq| image:: https://img.shields.io/requires/github/marrow/WebCore.svg
    :target: https://requires.io/github/marrow/WebCore/requirements/?branch=master
    :alt: Status of release dependencies.

.. |developstatus| image:: http://img.shields.io/travis/marrow/WebCore/develop.svg?style=flat
    :target: https://travis-ci.org/marrow/WebCore/branches
    :alt: Development build status.

.. |developcover| image:: http://img.shields.io/codecov/c/github/marrow/WebCore/develop.svg?style=flat
    :target: https://codecov.io/github/marrow/WebCore?branch=develop
    :alt: Development test coverage.

.. |developreq| image:: https://img.shields.io/requires/github/marrow/WebCore.svg
    :target: https://requires.io/github/marrow/WebCore/requirements/?branch=develop
    :alt: Status of development dependencies.

.. |issuecount| image:: http://img.shields.io/github/issues-raw/marrow/WebCore.svg?style=flat
    :target: https://github.com/marrow/WebCore/issues
    :alt: Github Issues

.. |ghsince| image:: https://img.shields.io/github/commits-since/marrow/WebCore/2.0.3.svg
    :target: https://github.com/marrow/WebCore/commits/develop
    :alt: Changes since last release.

.. |ghtag| image:: https://img.shields.io/github/tag/marrow/WebCore.svg
    :target: https://github.com/marrow/WebCore/tree/2.0.3
    :alt: Latest Github tagged release.

.. |latestversion| image:: http://img.shields.io/pypi/v/WebCore.svg?style=flat
    :target: https://pypi.python.org/pypi/WebCore
    :alt: Latest released version.

.. |downloads| image:: http://img.shields.io/pypi/dw/WebCore.svg?style=flat
    :target: https://pypi.python.org/pypi/WebCore
    :alt: Downloads per week.

.. |cake| image:: http://img.shields.io/badge/cake-lie-1b87fb.svg?style=flat

