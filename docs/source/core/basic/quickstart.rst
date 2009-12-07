******************************
Creating a new Web Application
******************************

.. contents:: Table of Contents
   :depth: 2
   :local:


Light-Weight Applications
=========================

WebCore was designed from the ground up to be as flexible as possible without restricting the more advanced features to the more advanced ways of building applications.  All features of the framework are available in the simplest of applications.

The fastest way to get started with WebCore is to create the universal example application: hello world.

Create a new file in your virtual environment, ``hello.py``, and enter the following:

.. code-block:: python

   from web.core import Controller
   
   class RootController(Controller):
       def index(self):
           return 'Hello world!'
   
   if __name__ == '__main__':
       import logging
       from paste import httpserver
       from web.core import Application

       logging.basicConfig(level=logging.INFO)

       app = Application.factory(root=RootController, **{
               'debug': False,
               'web.sessions': False,
               'web.widgets': False,
               'web.sessions': False,
               'web.profile': False,
               'web.static': False,
               'web.compress': False
           })

       httpserver.serve(app, host='127.0.0.1', port='8080')

Run this application from a command prompt:

.. code-block:: bash

   (core)$ python hello.py
   INFO:web.core.application:factory:Preparing WebCore WSGI middleware stack.
   INFO:web.core.application:factory:WebCore WSGI middleware stack ready.
   serving on http://127.0.0.1:8080

Now open up a web browser to the URL given on the last line.  Hello world!


Each Section Explained
----------------------

First we define a controller:

.. code-block:: python

   from web.core import Controller

The Controller class defines the object-dispatch behaviour most applications will use.  It allows you to quickly prototype your application's structure without having to worry about decorators, regular expression URL mapping, or any of the nitty-gritty details most other frameworks require.

.. code-block:: python

   class RootController(Controller):
       def index(self):
           return 'Hello world!'

This is our main controller.  It defines a single method, index, which is called if no other method is given in the URL.  It returns the plain string "Hello world!" to the web browser.

.. code-block:: python

   if __name__ == '__main__':
       import logging
       from paste import httpserver
       from web.core import Application

If this script is run as a Python application from the command line (rather than imported by another script) code within this block is run.  First we import a few useful modules for us to configure and run a web server.

.. code-block:: python

   logging.basicConfig(level=logging.INFO)

Set the Python logging level to INFO.  The DEBUG level is useful if you are trying to diagnose a problem, but the output is very verbose.

.. code-block:: python

   app = Application.factory(root=RootController, **{
           'debug': False
           'web.sessions': False,
           'web.widgets': False,
           'web.sessions': False,
           'web.profile': False,
           'web.static': False,
           'web.compress': False
       })

Here we tell WebCore which controller to use as the root and the options we want to use.  For this test, we disable everything.

.. code-block:: python

   httpserver.serve(app, host='127.0.0.1', port='8080')

This starts a web server on the loopback interface, port 8080.


Packaged Applications
=====================

Packaged applications have the benefit of generally being more structured, better organized, can be packaged and deployed easily, and have the benefit of being able to utilize INI file configuration.

The fastest way to get started with a package is using the ``paster create`` command:

.. code-block:: bash

   (core)$ paster create HelloWorld
   Selected and implied templates:
     PasteScript#basic_package  A basic setuptools-enabled package

   Variables:
     egg:      HelloWorld
     package:  helloworld
     project:  HelloWorld
   Enter version (Version (like 0.1)) ['']: 
   Enter description (One-line description of the package) ['']: 
   Enter long_description (Multi-line description (in reST)) ['']: 
   Enter keywords (Space-separated keywords/tags) ['']: 
   Enter author (Author name) ['']: 
   Enter author_email (Author email) ['']: 
   Enter url (URL of homepage) ['']: 
   Enter license_name (License name) ['']: 
   Enter zip_safe (True/False: if the package can be distributed as a .zip file) [False]: 
   Creating template basic_package
   Creating directory ./HelloWorld
     Recursing into +package+
       Creating ./HelloWorld/helloworld/
       Copying __init__.py to ./HelloWorld/helloworld/__init__.py
     Copying setup.cfg to ./HelloWorld/setup.cfg
     Copying setup.py_tmpl to ./HelloWorld/setup.py
   Running /Users/amcgregor/Projects/WebCore/bin/python setup.py egg_info

Now that you have a package, stored in the ``HelloWorld`` folder, let's create some useful folders to help organize our project and then move the ``helloworld.py`` file we created above into the package:

.. code-block:: bash

   (core)$ mkdir HelloWorld/helloworld/{controllers,model,lib,public,templates}
   (core)$ touch HelloWorld/helloworld/__init__.py HelloWorld/helloworld/{controllers,model,lib,templates}/__init__.py
   (core)$ mv helloworld.py HelloWorld/helloworld/controllers/root.py
   (core)$ cd HelloWorld


setup.py Dependancies & Other
-----------------------------

The ``setup.py`` file defines package dependancies, meta-data, namespace packages, and a whole lot more.  You should update the ``install_requires`` line to include WebCore and any other package you will be using (Beaker, Genshi, and SQLAlchemy are a good start).  You'll also want to change or add the following line in the ``setup()`` call:

.. code-block:: python

   paster_plugins = ['PasteScript', 'WebCore']

This will allow you to make use of WebCore's interactive shell feature.

When you are satisfied with your project's meta-data, install your project in development mode:

.. code-block:: bash

   (core)$ python setup.py develop

This will register your package globally (adding it to the Python search path) and automatically pull in and install any of the dependancies you have defined.  This needs to be done to allow WebCore to find the root controller you configure in the next step as well as for TemplateInterface to find the templates you wish to use.


Development Configuration
-------------------------

Create a file called ``development.ini`` inside the project folder:

.. code-block:: ini

   [server:main]
   use = egg:Paste#http
   host = 127.0.0.1
   port = 8080

   [app:main]
   use = egg:WebCore
   debug = False

   web.root = helloworld.controllers.root:RootController

   web.sessions = False
   web.widgets = False
   web.sessions = False
   web.profile = False
   web.static = False
   web.compress = False
   
   [loggers]
   keys = root

   [handlers]
   keys = console

   [formatters]
   keys = generic

   [logger_root]
   level = INFO
   handlers = console
   
   [handler_console]
   class = StreamHandler
   args = (sys.stderr,)
   level = NOTSET
   formatter = generic

   [formatter_generic]
   format = %(asctime)s %(levelname)-5.5s [%(name)s] %(message)s

The ``[server:main]`` section replicates the functionality of the ``httpserver`` line and the ``[app:main]`` section replicates the options passed to ``Application.factory``.  Everything from the ``[loggers]`` section down configures the logging level, destination, and format for Python ``logging`` module messages.

To run your web application you can now issue the following command:

.. code-block:: bash

   (core)$ paster serve --reload development.ini

Passing the ``--reload`` argument tells the Paster web server to monitor the files in the project for modification and automatically restart the server to make the changes live.  You can now access the application from a web browser.

To continue development and add database models and templates to your application, see the respective sections of this documentation.


Graphical Application Creation
==============================

TBD.
