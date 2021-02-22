# WebCore

	© 2006-2021 Alice Bevan-McGregor and contributors.

	https://github.com/marrow/WebCore

	|latestversion|
	|ghtag|
	|downloads|
	|masterstatus|
	|mastercover|
	|masterreq|
	|ghwatch|
	|ghstar|


1. [What is WebCore?](#what-is-webcore)

   1.1. [Token Minimal Example](#token-minimal-example)

2. [Installation](#installation)

   2.1. [Dependencies and Extras](#dependencies-and-extras)

   2.2. [Development Version](#development-version)

3. [Basic Concepts](#basic-concepts)

   3.1. [Application](#application)

   3.2. [Context](#context)

   3.3. [Endpoints](#endpoints)

4. [Plugins and Namespaces](#plugins-and-namespaces)

5. [Version History](#version-history)

6. [License](#license)


## What is WebCore?

WebCore is a Python web application *nanoframework*, a fraction of the size of competing *microframeworks*, and culmination of more than twenty years of web development experience. It provides a clean API for standard points of _extension_ while encouraging structured separation and isolation of application components, exposing *Pythonic* APIs to the web.

The framework totals a few hundred lines of code, excluding blank lines, comments, and documentation, containing more comments and lines of documentation than lines of executable code. It utilizes an extension API to provide as much—*or as little*—functionality as you require to build your solution. Constructed to be easy to test, adapt, and use; any developer familiar with programming, not just Python programming, and armed with the [WSGI specification](https://www.python.org/dev/peps/pep-3333/) should be able to read and understand the entirety of the framework over the course of an evening.

Because WebCore is "bare-bones," a [solid understanding of HTTP](https://www.oreilly.com/library/view/http-the-definitive/1565925092/), the "language" WebCore speaks to browsers and other clients, is **strongly** recommended. A minimal grasp of [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) concepts will also be greatly beneficial, to help understand how to structure your own APIs utilizing this best practice.

Where other application frameworks are "highly opinionated,” expressly specifying the database layer, form layer, or template engine, and often providing their own for your application to use—*WebCore has virtually no opinions.* (An 
off-colour analogy the author frequently uses is: _as opinionated as a coma patient._) As a result, it is substantially smaller and more efficient than monolithic frameworks such as Django or Pyramid.

Bring your favourite—or simply most familiar—libraries along with you.\
Your application should be written in Python, _not framework_.


### Token Minimal Example

Really; **this is it**:

```python
from web.core import Application

Application("Hi.").serve('wsgiref')
```

The `Application` class represents a standard Python [WSGI application](https://www.python.org/dev/peps/pep-3333/), its instances the invokable speaking WSGI. The rest is up to you to select and arrange the components that best fit your own needs. [Many additional examples](https://github.com/marrow/WebCore/tree/master/example), ranging in complexity, are provided within the codebase.


## Installation

Installing WebCore is easy given an existing installation of Python. Installing Python is beyond the scope of this document, [please follow the official guide](https://wiki.python.org/moin/BeginnersGuide#Getting_Python). With a Python installation in hand execute the following in a terminal to install WebCore and its dependencies.

```sh
pip3 install WebCore
```

**Note:** We *strongly* recommend always using a container, virtualization, or sandboxing environment of some kind when developing using Python; installing things system-wide is yucky for a variety of reasons. We prefer light-weight native [`venv`](https://docs.python.org/3/library/venv.html) (formerly [`virtualenv`](https://virtualenv.pypa.io/)), others prefer solutions as robust as [Docker](https://www.docker.com) or [Vagrant](http://www.vagrantup.com).

If you add `WebCore` to your own project’s `install_requires` (or other dependency) [metadata](https://packaging.python.org/guides/distributing-packages-using-setuptools/#install-requires), WebCore will be automatically installed and made available when your own application, library, or extra is installed.

We recommend pinning version numbers to ensure there are no unintentional side-effects when updating. Use `WebCore~=3.0.0` to get all bug fixes for the current release while ensuring that larger, potentially incompatible, changes are not installed.


### Dependencies and Extras

Other than requiring minimum Python language compatibility with Python 3.8, WebCore has a spartan set of required _third-party_ packages that must be installed in order to function, only two of which are third-party:

* [`marrow.package`](https://github.com/marrow/package) handling plugin discovery, enumeration, and management, including dependency graph resolution.

* [`typeguard`](https://typeguard.readthedocs.io/) providing annotation-based type checking at runtime; the overhead of which can be eliminated if Python is run with [optimizations enabled](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONOPTIMIZE).

* [`web.dispatch`](https://github.com/marrow/web.dispatch) — A utility library implementing primitives useful for implementation of a ["dispatch" protocol](https://github.com/marrow/protocols/tree/master/dispatch#readme).

* [`WebOb`](http://webob.org) providing HTTP request, response, and status code exception helpers. 

These do not have additional dependencies of their own. All other dependencies will be application–determined; choice of template engine, database layer, session storage mechanism, and even dispatch method are left entirely up to the developer making use of the framework.

Provided are a number of optional `extras` requirements, which you can define using a comma-separated list appended to the package name during installation from the command-line, or within your own package's `install_requires`. For example, to install a typical set of development tools at the same time as WebCore, run:


```sh
pip3 install 'WebCore[development]'
```

Quotes may be required (depending on shell) to avoid automatic “shell expansion”, which would produce incorrect results. The available extras are:

- `development` -- this installs a recommended set of development-time packages, including:
	- [`pytest`](http://pytest.org/) and a suite of plugins for it,
	- The [`backlash`](https://github.com/TurboGears/backlash) interactive debugger (used by the optional `DebugExtension`),
	- A [`web.dispatch.object`](https://github.com/marrow/web.dispatch.object) object-oriented dispatch implementation well suited to rapid prototyping,
	- The comprehensive `ptipython` upgraded REPL shell combining [`ptpython`](https://github.com/prompt-toolkit/ptpython#readme) and the [`ipython`](https://ipython.org) Jupyter core.
	- The [`waitress`](https://github.com/Pylons/waitress) development web server.
	- And [`e`](https://pypi.org/project/e/).

#### Dispatch Mechanisms

The default choices for dispatch are allowed as extras:

- `object` -- install the object-oriented “object dispatch” mechanism. Object dispatch essentially treats classes as directories and their methods as files, for a more filesystem-centric perspective. This mechanism is also included in the default `development` set of dependencies.

- `rest` or `resource` -- an object-oriented dispatch mechanism similar to Object Dispatch, excepting that the base primitives are collections and resources, not just bare addressable endpoints, and methods correspond to HTTP verbs.

- `route` -- a hierarchical regular expression-based routing dispatch mechanism, with optimized handling of static path segments.


#### Front-End Web Servers

You can also name a supported server bridge as an extra. Currently available bridges with third-party dependencies include:

- `bjoern` -- a fast and [ultra-lightweight `libev`-based WSGI server](https://github.com/jonashaag/bjoern#readme).

- `eventlet` -- a [highly scalable non-blocking](http://eventlet.net) front-end.

- `flup` -- [a FastCGI bridge](https://www.saddi.com/software/flup/) well suited to production use. (Includes other front-end bridges and utilities as well.) This is one step shy of utilizing [uWSGI](https://uwsgi-docs.readthedocs.io/).

- `waitress` -- the recommended [development-time web server](https://docs.pylonsproject.org/projects/waitress/en/latest/), though the dependency-free `wsgiref` front-end can be used.

- `tornado` -- [a high-performance asynchronous server](https://www.tornadoweb.org/) developed by FriendFeed.


#### Serialization / Deserialization

There are additional extras covering a few additional RESTful content serializations:

- `bson` -- [Binary JSON](http://bsonspec.org) and [MongoDB-extended JSON](https://docs.mongodb.com/manual/reference/mongodb-extended-json/) encoding/decoding. If the `pymongo` package is installed its JSON serializer and deserializer will be automatically utilized in preference to Python’s standard one, permitting serialization and deserialization of many additional datatypes beyond pure JSON.

- `yaml` -- [Yet Another Markup Language](https://yaml.org), a capable text-based serialization format able to represent rich datatypes, multiple records, and streams of records, in addition to cross-references within the serialized data.


### Development Version

|developstatus|
|developcover|
|ghsince|
|issuecount|
|ghfork|

Development takes place on [GitHub](https://github.com/) in the [WebCore](https://github.com/marrow/WebCore/) project. Issue tracking, documentation, and downloads are provided there. Development chat (both development of WebCore and chat for users using WebCore to develop their own solutions) is graciously provided by [Freenode](ircs://chat.freenode.net:6697/#webcore) in the `#webcore` channel.

Installing the current development version requires [Git](https://git-scm.com/), a distributed source code management system. If you have Git you can run the following to download and *link* the development version into your Python runtime:

```sh
git clone https://github.com/marrow/WebCore.git
(cd WebCore; pip install -e .)
```

The parenthesis make the change in current working directory temporary, only impacting the associated `pip` invocation. You can then upgrade to the latest version at any time:

```sh
(cd WebCore; git pull; pip install -e .)
```

Extra dependencies can be declared the same as per packaged installation, remembering to quote the argument due to use of shell-expansion square brackets:

```sh
(cd WebCore; pip install -e '.[development]')
```

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes, and submit a pull request. This process is beyond the scope of this documentation; for more information see [GitHub's documentation](http://help.github.com/). There are [additional ways to contribute to the project](https://mongo.webcore.io/contributing) if code isn’t your strength.


## Basic Concepts

### Application

The `Application` class is the primary entry point for the web framework. You are free to subclass this to implement extension callback methods for customizations unique to your own application.

The constructor takes up to three arguments:

<dl><dt><code>root</code>
<dd>The object to use as the entry point for web application dispatch, <code>/</code>, and the only argument that can be supplied positionally.
<dt><code>extensions</code>
<dd>A list of extensions to use with your application.
<dt><code>logging</code>
<dd><code></code>
</dl>


- `root` -- `/` requests.

- `extensions` -- 

- `logging` -- the name of a logging level as a string, or a Python `logging` [dictionary configuration](https://docs.python.org/3/library/logging.config.html#dictionary-schema-details).

The "root controller" is used as the starting point for dispatch resolution of the endpoint for a request, see the [Controllers](#) section below for details on what can be used here, but it's basically anything.

By default the `BaseExtension`, providing basic request and response objects and basic views, is always enabled for your application, has no configuration, and does not need to be instantiated yourself. Other extensions should be instantiated and passed in the `extensions` list.

Logging configuration offers two choices: simple "global logging level" by defining `logging` as a dictionary only containing a `level` key naming the level to set, or full `logging.config.dictConfig` configuration. Passing only a level is equivalent to running `logging.basicConfig`.

This configuration can entirely come from YAML, for example::

root: !!python/name:web.app.example.RootController

extensions:
		- !!python/object:web.ext.debug.DebugExtension
		- !!python/object:web.ext.analytics.AnalyticsExtension
		- !!python/object:web.ext.annotation:AnnotationExtension

		logging:
		level: debug

		This would make managing complex extension configuration easier. One way to invoke WebCore with a configuration like this, while allowing for a distinction between production and development environments and use under ModWSGI would be::

		import yaml
		from web.core import Application

		fname = 'development.yaml' if __debug__ else 'production.yaml'
		with open(fname, 'r', encoding='utf-8') as fh:
		config = yaml.load(fh)

		app = Application(**config)

		if __name__ == "__main__":
		app.serve('wsgiref')

		Now, running `python run.py` (if saved as `run.py`) would serve the `development.yaml` configuration, and running as `python -O run.py` (optimization enabled) or with `PYTHONOPTIMIZE=1` set in the environment will utilize the `production.yaml` file.

		WebCore is highly aware running with optimizations enabled, eliminating many of the expensive validation checks that are only really useful in development. For example, calling an endpoint with invalid arguments will `404` with a friendly warning in development, but `500` in production as the `TypeError` is not preemptively checked and caught; this is one of the most expensive validation checks. Feel free to browse the code looking for `if __debug__` blocks to see what else changes in "production mode".

		The order you define the extensions in does not matter; they declare dependencies and will be automatically dependency-ordered when collecting callbacks. Please see the `extension.py` example for additional information on what you can do with them.


### Context

The overall application has an `ApplicationContext` associated with it. This object is passed around to the various extension callbacks and acts as an attribute access dictionary. (All of the typical dictionary methods will work, and the keys can be accessed as attributes instead, saving some typing.) During the processing of a request a subclass is constructed called `RequestContext` and in-request extension callbacks, and your controller endpoints, are given a reference to this instance.

The attributes present in the base `ApplicationContext` are:

- `app` -- a reference to the `Application` instance

- `root` -- the original object passed when constructing the `Application` instance

- `extension` -- the `WebExtensions` extension registry

- `dispatch` -- the `WebDispatchers` dispatch protocol bridge and plugin registry

- `view` -- the `WebViews` view handler registry

Extensions would access these during `start` and `stop` events, for example to register new view handlers.

The attributes present in the `RequestContext` (added by WebCore itself or the `BaseExtension` during request processing) are:

- `environ` -- the WSGI request environment as passed to WebCore's WSGI handler

- `request` -- a `webob.Request` representing the current HTTP request

- `response` -- a `webob.Response` object corresponding to the response WebCore will return

- `path` -- a list of dispatch steps represented by tuples of `(handler, script_name)`

Additional attributes may be added by other extensions.


### Endpoints

> Controllers, Endpoints, Dispatch, Oh My!

“Controllers” and, more generally, *callable endpoints*, are functions or methods called to process a request and return a value for view processing, or raise an exception. Non-method callables are passed the context as a first argument; methods are assumed to have access via `self` as the context will have been passed positionally to the class constructor.

*Callable endpoints* are additionally passed any unprocessed path elements as _positional_ parameters, and a combination of query string arguments (`GET` values) and form-encoded body elements (`POST` values) as _keyword_ arguments, with arguments from the request body taking precedence and duplicated keys being passed as a list of values. These endpoints may return any value there is a view registered for, see the [docstring of the view manager](https://github.com/marrow/WebCore/blob/develop/web/core/view.py?ts=4) for details.

*Static endpoints*, on the other hand, are non-callable objects that can be processed by a view. The very first example at the top of this document relies on the fact that there is a view to handle strings, both static, and as returned by a *callable endpoint* such as:

```python
def hello(context) -> str:
	return "Hello world!"
```

To allow for customization of the name, you would write this endpoint as:

```python
def hello(context, name:str="world") -> str:
	return f"Hello {name}!"
```

As noted in the Application section, when Python is run with optimizations enabled (`-O` or `PYTHONOPTIMIZE` set) unknown arguments being passed (unknown query string arguments or form values) will result in a `TypeError` being raised and thus a `500 Internal Server Error` due to the uncaught exception. In development (without optimizations) a `404 Not Found` error with a message indicating the mismatched values will be the result. You can use `*args` and `**kwargs` to capture any otherwise undefined positional and keyword arguments, or use an extension to mutate the incoming data and strip invalid arguments prior to the endpoint being called.

That "hello world" endpoint, however, may be called in _one of several different ways_, as no other restrictions have been put in place:

- `GET /` -- Hello world! (Default used.)

- `GET /Alice` -- Hello Alice! (Passed positionally.)

- `GET /?name=Bob` -- Hello Bob! (Via query string assignment.)

- `POST /` submitting a form with a `name` field and value of `Eve` -- Hello Eve! (Via form-encoded body assignment.)

	Other HTTP verbs will work as well, but a form-encoded body is only expected and processed on `POST` requests.

If you wish to forbid positional population of endpoint arguments, you can use Python’s native syntax to declare them [_keyword-only_](https://docs.python.org/3/tutorial/controlflow.html#keyword-only-arguments). This would prevent the second `GET` example above from working.

```python
def hello(context, *, name:str="world") -> str:
	return f"Hello {name}!"
```

The process of finding the endpoint to use to process a request is called *dispatch*. There are a number of forms of dispatch available, some should be immediately familiar. In most cases, dispatch completes upon reaching an executable object, such as a function or method, or when the dispatcher feels it has “gone as far as it can”, and the dispatcher in use may be re-negotiated as dispatch _descends_.

- **Object dispatch.** This is the default (providided by the `web.dispatch.object <https://github.com/marrow/web.dispatch.object>`__ package) form of dispatch for WebCore, and is also utilized by several other frameworks such as TurboGears. Essentially each path element is looked up as an attribute of the previously looked up object treating a path such as `/foo/bar/baz` as an attempt to resolve the Python reference `root.foo.bar.baz`. This is quite flexible, allowing easy redirection of descent using Python-standard protocols such as `__getattr__` methods, use of lazy evaluation descriptors, etc., etc.

- **Registered routes.** This will likely be the approach most familiar to developers switching from PHP frameworks or who have used any of the major macro- or micro-frameworks in Python such as Django, Flask, etc. You explicitly map URLs, generally using a regular expression or regular expression short-hand, to specific callable endpoints. Often this is a accomplished using a decorator. WebCore offers this form of dispatch throuhg the `web.dispatch.route <https://github.com/marrow/web.dispatch.route>`__ package.

- **Traversal.** This is similar to object dispatch, but descending through mapping keys. The previous example then translates to `root['foo']['bar']['baz']`, allowing managed descent through the `__getitem__` protocol. This is one of the methods (the other being routes) provided by Pyramid. We offer this form of dispatch through the `web.dispatch.traversal <https://github.com/marrow/web.dispatch.traversal>`__ package.

	There may be other dispatchers available and the protocol allows for "dispatch middleware" to offer even more flexible approaches to endpoint lookup. The dispatch protocol itself is framework agnostic (these example dispatchers are in no way WebCore-specific) and `has its own documentation <https://github.com/marrow/protocols/blob/master/dispatch/README.md>`__.


## Plugins and Namespaces

WebCore recommends registration of extensions and other plugins as Python-standard `entry_points` references. Please see the `relevant setuptools documentation <https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins>`__ for details on this process. Additionally, WebCore marks package namespaces for shared use. The namespaces used, and their purposes, are:

- `web` -- the top level shared namespace for WebCore and WebCore accessories

- `web.app` -- a namespace for reusable application components and your own use

- `web.ext` -- a namespace for WebCore extensions; your own can be placed here

- `web.server` -- light-weight WSGI server adapters; your own WSGI server can define a dependency-free adapter here, for example

The plugin namespaces follow a similar pattern:

- `web.app` -- re-usable components you can attach to your own controller trees

- `web.extension` -- extensions registered by name and "provides" tag

- `web.server` -- similarly, server adapters registered by name

WebCore also makes use of the `web.dispatch` namespace to look up dispatchers. Other WebCore-related packages and extensions may make use of other plugin namespaces. Have a gander at WebCore's `setup.py` file for an example of how to register plugins this way, and copy the `__init__.py` file from the `web` package into the overlay in your own package (and declare such in your `setup.py` package metadata as the `namespace_packages` argument) to participate in the Python package namespaces.


## Version History

### Version 3.0

* Documentation returned to Markdown.
* Python 3 namespace packaging.
* Endpoint argument collection provided a dedicated extension callback.

### Version 2.0

- A complete modernization rewrite of WebCore, from the ground up.
- Features multiple extension interfaces to extend registered view handlers and provide a uniform callback mechanism.
- Standard usage makes use of no superglobals or "thread locals", instead relying on a context object collaboratively populated by extensions.
- WebCore's former "dialect" system is now dispatch.

### Version 2.0.1

- Thanks Pypi.

### Version 2.0.2

- Corrected argument specification for `transform` extension callbacks, fixing `AnnotationExtension` usage as per `#163 <https://github.com/marrow/WebCore/issues/163>`__.
- Additional source-level documentation and expanded examples.
- An excessively large number of additional WSGI server adapters; now supported are: waitress, `tornado <http://s.webcore.io/aIaN>`__, `fcgi <http://s.webcore.io/fhVY>`__, `cherrypy <http://s.webcore.io/aIoF>`__, `appengine <http://s.webcore.io/aIic>`__, `paste <http://s.webcore.io/aIdT>`__, `eventlet <http://s.webcore.io/aIaa>`__, `gevent <http://s.webcore.io/aIpU>`__, `diesel <http://s.webcore.io/aIg2>`_, and `bjoern <http://s.webcore.io/aIne>`__. Each is available as an `extras_require` by the same name which will pull in the required third-party dependency.

### Version 2.0.3

- Argument processing moved out of `web.core` into extension `mutate` handlers. Features improved rich unflattening of query string and form encoded body parameters. Configurable behaviour. For details, see: `web/ext/args.py <https://github.com/marrow/WebCore/blob/develop/web/ext/args.py>`__
- [Extensively documented](https://github.com/marrow/WebCore/blob/develop/web/ext/acl.py) access control list extension validating endpoint security and return value permission using context-aware predicates.
- The ability for extensions to define additional callbacks for collection.
- The `DatabaseExtension` (formerly `DBExtension`) has been moved into `its own repository <https://github.com/marrow/web.db>`__.
- Content negotiation endpoint return value serialization, with pluggable `dumps` registry.
- Complete unit test coverage.


## License

WebCore has been released under the MIT Open Source license.

### The MIT License

Copyright © 2006-2021 Alice Bevan-McGregor and contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



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


*[API]: Application Programming Interface
*[RFC]: Request For Proposal
*[HTTP]: Hypertext Transfer Protocol
*[PEP]: Python Enhancement Proposal
*[WSGI]: Web Server Gateway Interface
*[REST]: Representational State Transfer
