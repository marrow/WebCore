.. _templating-section:

**************************
Templating & Serialization
**************************

.. contents:: Table of Contents
   :depth: 2
   :local:


Using Templates
===============

To use templates your controller methods return a 2-tuple or 3-tuple::

   (template_name, data)
   (template_name, data, template_options)

You can omit the brackets when returning from your controller.

``template_name``
   A string in one of the following formats:
   
   * ``package.subpackage.filename`` -- The extension will be auto-detected if possible.
   * ``package.subpackage/filename.ext`` -- Use this if the extension can not be auto-detected or if your templates folder is not a Python package.
   * ``/absolute/path/filename.ext``
   * ``./relative/filename.ext`` or ``../relative/filename.ext``
   
   Any of the above can be prefixed with the name of an engine and a colon to override the default engine defined in your configuration.
   
   Relative paths are relative to the working directory your web application was run within.

``data``
   A dictionary of values to pass to the template.

``template_options``
   A dictionary of arguments to supply to the template renderer.

An example controller method which passes the name given as an argument to the controller to a template:

.. code-block:: python

   def hello(self, name="world"):
       return "helloworld.templates.hello", dict(name=name)


Alternate Templating Languages
==============================

The default templating language is Genshi, however there are many others available.  If you want to default all of your controller methods (that use templates) to another language, define the following in your configuration:

.. code-block:: ini

   web.templating.engine = jinja2

You can also override the templating engine on a per-template basis by prefixing the name of the templating engine to the name of the template::

   "jinja2:helloworld.templates.hello"


Returning Serialized Data
=========================

The Common Template Interface includes a number of data serialization formats out-of-the-box.  The most useful ones for web development include:

``bencode``
   The serialization format used in Bittorrent with parsers in virtually every language available.  Offers a few advantages over other serialization formats.  `Described on Wikipedia <http://en.wikipedia.org/wiki/Bencode>`_.

``json``
   Java Script Object Notation is best for interactive sites as JavaScript can parse the data natively.
   
   JSON serialization is included in Python 2.6; in Python 2.5 you will need to install the ``simplejson`` module and include it in your project's ``install_requires``.

``yaml``
   "Yet Another Markup Language" is a rich, human-readable, and whitespace-sensitive serialization format `described here <http://www.yaml.org/>`_.

Others include the Python ``marshal`` and ``pickle`` formats, but those should be used with caution as they can contain executable code.

To use any of these serialization formats specify the name of the format and a single colon in your returned template name with the data to serialize as the second part of the 2-tuple.  E.g.:

.. code-block:: python

   def index(self):
       return "json:", dict(name="world")

Unlike full templating languages, you are not restricted to dictionaries as your top-level container:

.. code-block:: python

   def index(self):
       return "json:", ('name', ['bill', 'bob', 'world'])


Template Globals
================

WebCore includes a number of useful helpers in the ``web`` and global template namespaces:

``lookup``
   Look up the absolute path to the target template.

``relative``
   As per ``lookup``, but returns a relative path from the current template to the target.

``web.request``
   Access to the WSGI request object and environment.

``web.response``
   Access to the WSGI response object.

``web.cache``
   Access to the Beaker cache object.

``web.session``
   Access to the Beaker session object.

``web.i18n``
   Internationalization hooks.

``web.release``
   WebCore version information.



Defining Your Own
-----------------

To add objects to the global template namespace, extend the ``cti.middleware.registry`` dictionary:

.. code-block:: python

   from cti.middleware import registry
   
   registry.extend(dict(
           myglobal = "foo"
       ))

To add objects to the ``web`` namespace, extend the ``web.core.namespace`` dictionary:

.. code-block:: python

   import web
   
   web.core.namespace.extend(dict(
           myglobal = "foo"
       ))
