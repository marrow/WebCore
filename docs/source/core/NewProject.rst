.. highlight:: bash

Quick Start Guide
=================

:Status: Work in progress

.. contents:: Table of Contents
    :depth: 2

Assuming you have YAPWF installed, have your virtual environment activated (if you chose to create one), creating a new project is very simple.

The ``paster quickstart`` command will create a basic project directory for you to use to get started on your YAPWF application. You'll be prompted for the name of the project (this is the pretty name that human beings would appreciate), and the name of the package (this is the less-pretty name that Python will like).

    $ paster quickstart

Paster is a very powerful command with many options.  Paster, and any of the paster commands we will run, will print out full usage information if you add ``--help`` to the command line.  For this simple example, the following were our answers::

    Enter project name: HelloWorld
    Enter package name [helloworld]: helloworld
    Do you need to connect to a database? [yes]
    Which database engine do you prefer? [sqlalchemy]
    What is the database connection string? [sqlite:///development.db]
    Which templating engine do you prefer? [genshi]
    Will you be serving static support files (CSS, JS, images, etc.)? [yes]
    ...

This will create a new Python package and directory structure to support your application.

Let's go into our new folder and take a look around::

    $ cd heloworld
    $ ls
    development.ini  helloworld/  setup.cfg  setup.py
    
    $ ls heloworld
    __init__.py  controllers/  lib/  model/  public/  templates/

The ``setup.py`` file has a section which explicitly declares the dependencies of your application.   The quickstart template has a few built in dependencies, and as you add new Python libraries to your application's stack, you'll want to add them here too.

In order to make sure all those dependencies are installed you will want to run::

   $ python setup.py develop

Another key piece of YAPWF application setup infrastructure is the ``paster prepare`` command which takes a configuration file and runs ``lib/prepare.py`` in that context.   This allows you to use ``prepare.py`` to create database tables, pre-populate lookup or other required data into your database, and otherwise make things nice for people fist setting up your app.


Run the server
---------------

If this is the first time you're starting the application you have to run the following command to create and initialize your test database::

    $ paster prepare development.ini

This will create the database using the information stored in the ``development.ini`` file which by default makes single file SQLite database in the local file system called ``development.db``. In addition to creating the database, it runs whatever extra database loaders or other setup are defined in ``prepare.py``.

It also shows how you can add new data automatically to the database when you need to add bootstrap data of your own.

At this point your project should be operational, and you're ready to start up the application.  To start a YAPWF application, ``cd`` to the new directory (`helloworld`) and issue command ``paster serve`` to serve your new application::

    $ paster serve --reload development.ini

When using the Bourne Again (BASH) shell, you can simply execute the INI file as if it were an application::

    $ ./development.ini

Once running, point your web browser at http://localhost:8080/ and you'll see a nice welcome page with the a flash message and current time.  The paster command can be run from any directory as long as you give it a valid path to an INI file.  The INI file itself can be stored anywhere, too.

If you take a look at the code that quickstart created you'll see that there isn't much involved in getting up and running.

In particular, you'll want to check out the files directly involved in displaying this welcome page:

  * `development.ini` contains the system and database configuration for development.
  * `helloworld/controllers/root.py` contains the controller code to create the data for the welcome page along with usage examples for various framework features.
  * `helloworld/templates/index.html` is the template used to render the welcome page from the dictionary returned by the root controller. It's standard XHTML with some simple Python namespace attributes.
  * `helloworld/public/` is the place to hold static files such as images, JavaScript, or CSS.

You can easily edit development.ini to change the default server port used by the built-in web server::

  [server:main]
  ...
  port = 8080
  
Just change 8080 to 80, and you'll be serving your app up on a standard port (assuming your OS allows you to do this using your normal account, otherwise you will have to be a superuser).


Explore the rest of the quickstarted project code
----------------------------------------------------

Once your application is up and running it's probably a good time to take a look around the files that are generated automatically, so you know where things go.  The number of files created out-of-the-box is minimal, and they all have clear, well-defined purposes with source-level documentation aplenty.