.. highlight:: bash

Quickstarting a TurboGears 2 project
====================================

:Status: Work in progress

.. contents:: Table of Contents
    :depth: 2

Now we assume you've got TurboGears installed and, if you installed it in a
virtual environment, that your virtualenv is :ref:`activated <activate_virtualenv>`.
TurboGears 2 extends the ``paster`` command-line tool to provide a suite of tools for working with TurboGears 2 projects. A few will be touched upon in this tutorial, check the ``paster --help`` command for a full listing.

The very first tool you'll need is ``paster quickstart``, which initializes a TurboGears 2 project.
You can go to whatever directory you want and start a new TurboGears 2 project by typing::

  $ paster quickstart

The ``paster quickstart`` command will create a basic project directory for you to use to get started on your TurboGears 2 application. You'll be prompted for the name of the project (this is the pretty name that human beings would appreciate), and the name of the package (this is the less-pretty name that Python will like).

Here's what our choices for this tutorial look like::

    Enter project name: Helloworld
    Enter package name [helloworld]: helloworld
    Do you need authentication and authorization in this project? [yes]
    ...output...

This will create a new directory which contains a few files in a directory tree, with some code already set up for you.

Let's go in there and you can take a look around::

   $ cd Helloworld

The ``setup.py`` file has a section which explicitly declares the dependencies of your application.   The quickstart template has a few built in dependencies, and as you add new python libraries to your application's stack, you'll want to add them here too. 

Then in order to make sure all those dependencies are installed you will want to run:: 

   $ python setup.py develop
   

Another key piece of TG2 application setup infrastructure is the ``paster setup-app`` command which takes a configuration file and runs ``websetup.py`` in that context.   This allows you to use websetup.py to create database tables, pre-populate require data into your database, and otherwise make things nice for people fist setting up your app. 

.. note :: 

  If it's the first time you're going to use the application, and you told
  quickstart to include authentication+authorizaiton, you will *have* to
  run ``setup-app`` to set it up (e.g., create a test database)::
  
      $ paster setup-app development.ini



Run the server
---------------

If this is the first time you're starting the application you have to run the following command to create and initialize your test database::

    $ paster setup-app development.ini

This will create the database using the information stored in the development.ini file which by default makes single file SQLite database in the local file system. In addition to creating the database, it runs whatever extra database loaders or other setup are defined in websetup.py.  In a quickstarted project with Auth enabled it creates a couple of basic users, groups, and permissions for you to use as an example. 

It also shows how you can add new data automatically to the database when you need to add bootstrap data of your own. 

At this point your project should be operational, and you're ready to start up the app.   To start a TurboGears 2 app, ``cd`` to the new directory (`helloworld`) and issue command ``paster serve`` to serve your new application::

    $ paster serve development.ini

As soon as that's done point your browser at http://localhost:8080/ and you'll see a nice welcome page with the inform(flash) message and current time.

.. note::
    If you're exploring TurboGears 2 after using TurboGears 1 you may notice a few things:

      * The old config file `dev.cfg` file is now `development.ini`.
      * By default the ``paster serve`` command is not in auto-reload mode as the CherryPy server used to be.  If you also want your application to auto-reload whenever you change a source code file just add the ``--reload`` option to ``paster serve``::

          $ paster serve --reload development.ini

You might also notice that paster serve can be run from any directory as long as you give it the path to the right ini file.

If you take a look at the code that quickstart created you'll see that there isn't much involved in getting up and running.

In particular, you'll want to check out the files directly involved in displaying this welcome page:

  * `development.ini` contains the system configuration for development.
  * `helloworld/controllers/root.py` contains the controller code to create the data for the welcome page along with usage examples for various tg2 features.
  * `helloworld/templates/index.html` is the template turbogears uses to render the welcome page from the dictionary returned by the root controller. It's standard XHTML with some simple namespaced attributes.
  * `helloworld/public/` is the place to hold static files such as pictures, JavaScript, or CSS files.

You can easily edit development.ini to change the default server port used by the built-in web server::

  [server:main]
  ...
  port = 8080
  
Just change 8080 to 80, and you'll be serving your app up on a standard port (assuming your OS allows you to do this using your normal account).


Explore the rest of the quickstarted project code
----------------------------------------------------

Once you've got a quickstarted app going it's probably a good time to take a look around the files that are generated by quickstart so you know where things go. 


As you can see there are quite a few files generated. If you look inside them you'll discover that many of them are just stubs so that you'll have a standard place to put code as you build your project.
