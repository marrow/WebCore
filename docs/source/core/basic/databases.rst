.. _databases-section:

*********
Databases
*********

.. contents:: Table of Contents
   :depth: 2
   :local:


Configuring Database Connections
================================

To utilize a database connection from within your application, you need two things: a configuration, and a model.

Configuration is easy:

.. code-block:: ini

   db.connections = core

   db.core.engine = <engine>
   db.core.model = yourproject.model

Here's what each bit of this represents:

``db.connections``
   A comma-separated list of database connections.  The name used here is used as the prefix for the database-specific configuration.

``db.core.engine``
   Here you tell WebCore which database engine you wish to use.  Currently we support two: ``sqlalchemy`` and ``mongo``.

``db.core.model``
   A dot-notation reference to the Python module which contains your model.  Individual engines may have requirements about what needs to be in that module.


Using SQLAlchemy
================

SQLAlchemy has additional configuration options:

.. code-block:: ini

   db.core.sqlalchemy.url = sqlite:///development.db
   db.core.sqlalchemy.echo = False

``db.core.sqlalchemy.url``
   Specifies the back-end database engine to connect to.

``db.core.sqlalchemy.echo``
   Weather or not the raw SQL queries be displayed in the log.

SQLAlchemy has an extensive list of additional configuration parameters on `their site <http://www.sqlalchemy.org/docs/05/dbengine.html#database-engine-options>`_.


Your Model
----------

WebCore strongly suggests using SQLAlchemy's `declarative extension <http://www.sqlalchemy.org/docs/05/reference/ext/declarative.html>`_.  To get started quickly, create a new module called ``base.py`` inside your ``model`` package and paste the following in:

.. code-block:: python

   # encoding: utf-8

   from sqlalchemy.ext.declarative import declarative_base


   __all__ = ['Base']



   class DeclarativeEntity(object):
       @classmethod
       def get(cls, *args, **kw):
           from YOURPROJECT.model import session
           return session.query(cls).get(*args, **kw)


   Base = declarative_base(cls=DeclarativeEntity)

Replace ``YOURPROJECT`` with the name of your top-level package.  In the ``__init__.py`` file inside your ``model`` package, enter the following:

.. code-block:: python

   # encoding: utf-8

   from paste.registry import StackedObjectProxy

   # from YOURPROJECT.model.wiki import *


   metadata = Base.metadata
   session = StackedObjectProxy()



   def prepare():
       metadata.create_all()

   def populate(session, table):
       pass

The thread-local database session will be automatically placed in the ``session`` variable on each request.  The ``prepare`` function is called once the database engine has been configured, and ``populate`` is called once for each table that gets created in the database, allowing you to populate the database with stock data.

The commented-out import line is an example of how to include actual table structures from other files, allowing you to split your model logically into separate files.

Let's create a ``wiki.py`` file as an example data structure:

.. code-block:: python

   # encoding: utf-8

   from sqlalchemy import *
   from sqlalchemy.orm import *

   from .base import Base


   __all__ = ['Article']



   class Article(Base):
       __tablename__ = 'articles'
    
       name = Column(Unicode(250), primary_key=True)
       content = Column(UnicodeText)

You need to define ``__all__`` in your model modules to ensure the correct objects get imported into the ``__init__.py`` file.

For more information on how to use SQLAlchemy, see the relevant documentation on SQLAlchemy's `website <http://www.sqlalchemy.org/docs/05/index.html>`_.


Legacy Database Connections with SQLSoup
========================================

If you define ``db.*.sqlsoup = True`` in the configuration for your database connection, a ``soup`` object will be created within your model's module which will allow you to access legacy databases using SQLAlchemy's SQLSoup module.

For documentation on SQLSoup's capabilities, please see the relevant documentation on SQLAlchemy's `website <http://www.sqlalchemy.org/docs/05/reference/ext/sqlsoup.html>`_.


MongoDB
=======

TBD.
