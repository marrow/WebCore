.. _databases-section:

*********
Databases
*********

.. contents:: Table of Contents
   :depth: 2
   :local:


Configuring Database Connections
================================

To utilize a database connection from within your application, you need two
things: a configuration, and a model.

Configuration is easy:

.. code-block:: ini

   db.connections = core

   db.core.engine = <engine>
   db.core.model = yourproject.model

Here's what each bit of this represents:

``db.connections``
   A comma-separated list of database connections. The name used here is used
   as the prefix for the database-specific configuration. The name "core" is
   only used as an example -- it can be any string you want.

``db.core.engine``
   Here you tell WebCore which database engine you wish to use.
   Currently we support two: ``sqlalchemy`` and ``mongo``.

``db.core.model``
   A dot-notation reference to the Python module which contains your model.
   Individual engines may have requirements about what needs to be in that module.


Using SQLAlchemy
================

SQLAlchemy has additional configuration options:

.. code-block:: ini

   db.core.sqlalchemy.url = sqlite:///development.db
   db.core.sqlalchemy.echo = False

``db.core.sqlalchemy.url``
   Specifies the back-end database engine to connect to.

``db.core.sqlalchemy.echo``
   Whether or not the raw SQL queries should be displayed in the log.

SQLAlchemy has an extensive list of additional configuration parameters on
`their site <http://www.sqlalchemy.org/docs/dbengine.html#database-engine-options>`_.

.. note:: If you use MySQL, you should note that it usually requires some
          special settings to work properly with unicode (at least with the
          default driver). For that, you should append the ``charset=utf8`` and
          ``use_unicode=0`` options to the connect string.
          Please consult the
          `MySQL section <http://www.sqlalchemy.org/docs/dialects/mysql.html#character-sets>`_
          of the SQLAlchemy documentation for more information.


Your Model
----------

WebCore strongly suggests using SQLAlchemy's
`declarative extension <http://www.sqlalchemy.org/docs/reference/ext/declarative.html>`_.
To get started quickly, create a new module called ``model.py`` inside your
project's top level package and paste the following in:

.. code-block:: python

   from paste.registry import StackedObjectProxy
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.orm import *
   from sqlalchemy import *


   Base = declarative_base()
   metadata = Base.metadata
   session = StackedObjectProxy()

   class Article(Base):
       __tablename__ = 'articles'
    
       name = Column(Unicode(250), primary_key=True)
       content = Column(UnicodeText)


   def prepare():
       metadata.create_all()


   def populate(session, table):
       pass

The thread-local database session will be automatically placed in the ``session``
variable on each request.  The ``prepare`` function is called once the database
engine has been configured, and ``populate`` is called once for each table that
gets created in the database, allowing you to populate the database with stock data.

If your project has a lot of tables, you may want to split them into several
different modules. In that case, you should turn your model module into a
package instead. You should import the ``Base`` class into every module where
you define new declarative classes, and leave ``Base``, ``metadata``,
``session``, ``prepare`` and ``populate`` in the model package's ``__init__.py``
file. Common beginner mistakes include calling
:func:`~sqlalchemy.ext.declarative.declarative_base` more than
once or using more than one :class:`~sqlalchemy.schema.MetaData` instance for
the same database.

For more information on how to use SQLAlchemy, see the relevant documentation
on SQLAlchemy's `website <http://www.sqlalchemy.org/docs/>`_.


Legacy Database Connections with SQLSoup
========================================

If you define ``db.*.sqlsoup = True`` in the configuration for your database
connection, a ``soup`` object will be created within your ``model`` module
which will allow you to access legacy databases using SQLAlchemy's SQLSoup module.

For documentation on SQLSoup's capabilities, please see the relevant
documentation on SQLAlchemy's
`website <http://www.sqlalchemy.org/docs/reference/ext/sqlsoup.html>`_.


MongoDB
=======

`MongoDB <http://www.mongodb.org>`_ is an extremely powerful, efficient, and
capable schemaless no-SQL database.  It has excellent Python support.
To use it, declare a new database connection using the **mongo** engine and
something like the following in your INI file:

.. code-block:: ini

    db.core.model = coresite.model
    db.core.url = mongo://localhost/coresite

``db.core.url``
    Specifies the back-end database engine to connect to.


In your model module include something like the following:

.. code-block: python

    db = None

    users = None
    wiki = None
    history = None
    
    def prepare():
        global profiling, users, wiki, history
        
        users, wiki, history = db.users, db.wiki, db.history

This will assign handy top-level names for MongoDB collections.

For more information, see the
`documentation for PyMongo <http://api.mongodb.org/python/>`_.