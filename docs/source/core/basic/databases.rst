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

   db.X.engine = <engine>
   db.X.model = myapp.model

``X`` here is the identifier of your model. Use whatever name you want in its
place, and use a different identifier for each database you want to connect to.
Also, this and all the following examples assume that the top level package
name of your application is **myapp**.

Here's what each bit of this represents:

``db.connections``
   A comma-separated list of database connections. The name used here is used
   as the prefix for the database-specific configuration.

``db.X.engine``
   Here you tell WebCore which database engine you wish to use.
   Currently we support two: ``sqlalchemy`` and ``mongo``.

``db.X.model``
   A dot-notation reference to the Python module which contains your model.
   Individual engines may have requirements about what needs to be in that module.
   
   Example: ``db.core.model = myapp.model``

``db.X.url``
   The connection string that defines the location of the actual database.
   The format of this parameter varies based on the selected engine.


Using SQLAlchemy
================

SQLAlchemy is a library for interfacing with relational database management
systems (often referred to as SQL databases). It can be used in many possible
ways, from raw SQL to object relational mapping (ORM).
If you have no previous experience with SQLAlchemy, it is recommended that you
take the `tutorial <http://www.sqlalchemy.org/docs/orm/tutorial.html>`_ to
learn the basics.

The connection URLs for SQLAlchemy generally look like
``dialect+driver://user:pass@host/database``. They could also be as simple as
``sqlite:///``. For example, to configure a model named "core", you could add
this to your Paste ini file:

.. code-block:: ini

    db.connections = core
    db.core.engine = sqlalchemy
    db.core.model = myapp.model
    db.core.url = mysql+oursql://username:password@localhost/myapp
    db.core.ready = myapp.model:ready

``db.core.autocommit``
   If ``True``, don't start a transaction implicitly. If False, a transaction is
   implicitly started whenever a session is created. The default is ``False``.

``db.core.autoflush``
   If ``True``, flush all impending changes to the database after every command.
   If ``False``, changes are flushed all at once when
   :meth:`~sqlalchemy.orm.session.Session.commit` or
   :meth:`~sqlalchemy.orm.session.Session.flush` is called, or at the end of the
   request. The default is ``True``.

``db.core.ready``
  An optional dot-colon notation path to a callback.  This callback takes a single
  positional parameter, ``sessionmaker``, and is called after the database connection
  is configured.  If configuring directly in Python, you may pass a callable object
  directly.

Any options after ``db.X.sqlalchemy.`` will be passed directly to
:func:`~sqlalchemy.engine_from_config`. SQLAlchemy has an extensive list of
additional configuration parameters on
`their site <http://www.sqlalchemy.org/docs/core/engines.html#database-engine-options>`_.
Two very useful options deserve a mention here though:

``db.core.sqlalchemy.echo``
   Set to ``True`` to output all generated raw SQL to standard output.

``db.core.sqlalchemy.echo_pool``
   Set to ``True`` to output information on connection pool changes to standard output.

For more information on how to use SQLAlchemy, see the relevant documentation
on their `website <http://www.sqlalchemy.org/docs/>`_.

.. note:: For MySQL, the recommended driver is currently
          `oursql <http://packages.python.org/oursql/>`_.


An Example Model
----------------

It is strongly suggested that you define your models using SQLAlchemy's
`declarative extension <http://www.sqlalchemy.org/docs/orm/extensions/declarative.html>`_.
To get started quickly, create a new module in the ``myapp`` package called
``model.py`` paste the following in:

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
    
       id = Column(Integer, primary_key=True
       name = Column(Unicode(250), nullable=False)
       content = Column(UnicodeText, nullable=False)


   def ready(sessionmaker):
       metadata.create_all()

This example model defines a single table named **articles**. It contains three
columns, **id**, **name** and **content**. Of all the variables and functions
defined in the above example, only ``session`` is strictly required. The rest
are there to facilitate the use of table metadata and object relational mapping.

The ``Base`` class should be used as the base class of all your model classes.

The ``metadata`` variable contains information about the tables in your model.

The ``session`` variable is a thread-local proxy that is usable while your
application is processing a request.

The ``ready`` function, when referenced by the ``db.*.ready`` configuration
value, is executed after the database connection is prepared.
The ``metadata.create_all()`` call creates any tables missing from the database.


An example controller using SQLAlchemy
--------------------------------------

The following simple example shows how to handle listing, creation, updating
and deleting articles. The model from the previous section is assumed to be
at ``myapp.model`` and there should be a template at ``myapp/templates/``
by the name of ``articlelist.html``.

.. code-block:: python

    from webob.exc import HTTPFound
    from web.core import Controller
    
    from myapp.model import session, Article


    class ExampleController(Controller):
        def index(self):
            raise HTTPFound(location='list')        

        def list(self):
            articles = session.query(Article).all()
            return 'myapp.templates/articlelist.html', {'articles': articles}

        def create(self, **kwargs):
            session.add(Article(**kwargs))
            raise HTTPFound(location='list')

        def update(self, id, **kwargs):
            article = session.query(Article).get(id)
            if article:
                for key, value in kwargs.items():
                    setattr(article, key, value)
            raise HTTPFound(location='list')

        def delete(self, id):
            article = session.query(Article).get(id)
            if article:
                session.delete(article)
            raise HTTPFound(location='list')


Transactions
------------

Transactions are the "working units" of a relational database. Almost any
changes made to the database data while in a transaction can be reversed if
something goes wrong so that either all the changes are persisted or none of
them are. In a WebCore application, a transaction is automatically started for
you when you access the database. When the controller method returns a value,
the transaction is automatically committed. If instead an exception is raised
from the controller, the transaction is rolled back. All this means is that you
don't have to worry about managing transactions on your own. Just do your
inserts, updates and deletes and let WebCore handle the transactions for you.


Legacy Database Connections with SQLSoup
----------------------------------------

If you define ``db.X.sqlsoup = True`` in the configuration for your database
connection, a ``soup`` object will be created within your ``model`` module
which will allow you to access legacy databases using SQLAlchemy's SQLSoup module.

For documentation on SQLSoup's capabilities, please see the relevant
documentation on SQLAlchemy's
`website <http://www.sqlalchemy.org/docs/orm/extensions/sqlsoup.html>`_.


Models In Large Applications
----------------------------

If your application has a lot of tables, you may want to split your model into
several different modules. In that case, you should turn your model module into
a package instead. First, define ``Base``, ``metadata`` and ``session`` in the
package's ``__init__.py`` module. After that, import the model classes (or just
the modules themselves if you want) from all the other modules in the model
package. This is necessary for the tables to be properly included in the
metadata. Also, make sure you do it in this order to avoid circular import
problems.


Using MongoDB
=============

`MongoDB <http://www.mongodb.org>`_ is an extremely powerful, efficient, and
capable schemaless no-SQL database with excellent Python support.
To use it, declare a new database connection using the **mongo** engine and
something like the following in your INI file:

.. code-block:: ini

    db.core.engine = mongo
    db.core.model = myapp.model
    db.core.url = mongo://localhost/myapp
    db.core.ready = myapp.model:connected


In your model module include something like the following::

    db = None

    users = None
    wiki = None
    history = None
    
    def connected():
        global profiling, users, wiki, history
        
        users, wiki, history = db.users, db.wiki, db.history

This will assign handy top-level names for MongoDB collections.

For more information, see the
`documentation for PyMongo <http://api.mongodb.org/python/>`_.


Using multiple databases
========================

WebCore can easily support the use of multiple databases, regardless of their
type. For example, to configure three databases -- one PostgreSQL database, one
MongoDB database and one MySQL database, you could use a configuration like the
following:

.. code-block:: ini

    db.users.engine = sqlalchemy
    db.users.model = myapp.auth.model
    db.users.url = postgresql:///users

    db.wiki.model = myapp.wiki.model
    db.wiki.url = mongo://localhost/wiki

    db.history.engine = sqlalchemy
    db.history.model = myapp.history.model
    db.history.url = mysql+oursql://me:mypassword@localhost/history

    db.connections = users, wiki, history

The above configuration uses separate databases and models for users, wiki and
history. The models are completely independent of each other, and should be
built according to the instructions detailed in the previous sections.

.. note:: Two phase transactions are currently not supported. This will be
          rectified in a future version of WebCore.
