******************
Installing WebCore
******************

This document provides several methods of installing WebCore; the method you choose will depend on your level of experience and platform.

We recommend installing WebCore into a virtual environment which will prevent any interference with your system's installed packages and won't unknowingly upgrade any Python libraries that your system needs.

If you want to build packages of WebCore for your system please send an email to webcore-devel@webcore.org.

.. contents:: Table of Contents


Prerequisites
=============

  1. Python 2.5
  2. Setuptools
  3. virtualenv
  4. Application dependancies

Python
------

WebCore works with any version of Python 2.5 or later and less than 3.0. The most widely deployed version of python at the moment of this writing is version 2.5.  Python 3.0 is currently unsupported due to lack of support in many of our upstream packages, though we do look forward to support in the near future.

We recommend you use your system's default Python install or follow the instructions provided here: http://python.org/download/

If you don't know which version of python you have installed you can find out with the following command:

.. code-block:: bash

   $ python --version
   Python 2.5.2


Installing setuptools
---------------------

On Windows
^^^^^^^^^^

Download http://peak.telecommunity.com/dist/ez_setup.py and then run it from the command line.

On Unix
^^^^^^^

.. code-block:: bash

    $ wget http://peak.telecommunity.com/dist/ez_setup.py | sudo python

You may also use your system's package for setuptools, for example, on Gentoo:

.. code-block:: bash

    $ sudo emerge -av setuptools

On Debian or Ubuntu:

.. code-block:: bash

    $ sudo apt-get python-setuptools


Additional Packages
-------------------

Most packages are defined as dependancies within your own application, not the framework.  As such, the first time you prepare your web application's build environment (using `setup.py develop`) packages will be automatically downloaded an installed.

Object Relational Mapper Database Layer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: The installation of the database back-end is a topic outside of the scope of this document.

WebCore uses SQLAlchemy as its default ORM (Object Relational Mapper) layer, although a number of database libraries are supported.  SQLAlchemy maintains excellent documentation on all the `engines supported`_.

.. _engines supported: http://www.sqlalchemy.org/docs/05/reference/dialects/index.html

Cygwin users can't use sqlite as it does not include the necessary binary file (``sqlite3.dll``).  If you want to run Cygwin you'll need to install a different database.

The database layer will be installed automatically


Installing non-Python Dependencies
----------------------------------

You will most likely need a C compiler and the Python header files. Please see the appropriate section below.

Windows
^^^^^^^
You may want the `win32api`_ package as it provides some very useful tools for Windows developers, the first you will encounter is the ability to make virtualenv work with paths that contain spaces.

.. _win32api: http://starship.python.net/crew/mhammond/win32/

Cygwin
^^^^^^
You must perform all operations, including setup operations, within DOS command windows, not Cygwin command window.

MacOS X
^^^^^^^
Xcode is required to build some binary dependancies and is available on the OS X CD or from Apple's `developer site`_. 

.. _developer site: http://developer.apple.com/tools/xcode/

Debian, Ubuntu 
^^^^^^^^^^^^^^
Debian derived Linux versions require ``python-dev`` and ``build-essential``::

    $ sudo apt-get install python-dev
    $ sudo apt-get install build-essential

RedHat, Fedora, CentOS
^^^^^^^^^^^^^^^^^^^^^^
Fedora users will need the ``python-devel`` rpm::

    $ sudo yum install python-devel

Gentoo
^^^^^^
Nothing extra is required as Gentoo has a full development environment configured by default.

Other Linux and UNIX
^^^^^^^^^^^^^^^^^^^^
You'll need a working version of the GCC compiler installed, as well as the Python headers.  


Installing virtualenv
---------------------

We strongly advise you to install all your WebCore apps inside a virtual environment.  If you ask for support without a virtualenv to isolate your packages we will usually ask you to go get virtualenv before proceeding further.

``virtualenv`` is a tool that you can use to keep your Python path clean and tidy.  It allows you to install new packages and all of their dependencies into a clean working environment, thus eliminating the possibility that installing WebCore or some other new package will break your existing Python environment.

The other great advantage of virtualenv is that it allows you to run multiple versions of the same package in parallel which is great for running both the production version and the development version of an application on the same machine.

People with a systems administration background could consider virtualenv as a variation of an OS jail (chroot) which is also good for security as your installation is totally isolated. This makes virtualenv great for deploying production sites.

On Windows::

    easy_install virtualenv

On Unix:

.. code-block:: bash

    $ sudo easy_install virtualenv

Or without root privileges:

.. code-block:: bash

    $ easy_install --install-dir=$HOME/lib/python2.5/ --script-dir=$HOME/bin/ virtualenv

You should see output similar to:

.. code-block:: text

    Searching for virtualenv
    Reading http://pypi.python.org/simple/virtualenv/
    Best match: virtualenv X.Y.Z
    Downloading http://pypi.python.org/packages/2.5/v/virtualenv/virtualenv-X.Y.Z-py2.5.egg#md5=1db8cdd823739c79330a138327239551
    Processing virtualenv-X.Y.Z-py2.5.egg
    .....
    Processing dependencies for virtualenv
    Finished processing dependencies for virtualenv

Installing WebCore
==================

We provide several methods for installing WebCore which depend on the level of control you want over it:

    1. plain virtualenv
    2. development version

.. hint::
    Please note we are using ``core`` as the name of the virtual environment.  This is simply a convention in our documentation, the name of the virtualenv depends totally on the user and should be named according to the project it contains.

Basic Installation
------------------

First, ``cd`` to the directory where you want your virtual environment for WebCore. Note the virtualenv will be created as a subdirectory here.

Now create a new virtual environment named ``core``:

.. code-block:: bash

    $ virtualenv --no-site-packages core

that produces something like this::

     Using real prefix '/usr/local'
     New python executable in core/bin/python
     Installing setuptools............done.

.. _activate_virtualenv:

Activate your virtualenv 
^^^^^^^^^^^^^^^^^^^^^^^^
First go inside the virtualenv::

    $ cd core

On Windows you activate a virtualenv with the command::

    Scripts\activate.bat

On Unix you activate a virtualenv with the command:

.. code-block:: bash

    $ . bin/activate

If you are on Unix your prompt should change to indicate that you're in a virtualenv.
It will look something like this::

    (core)username@host:~/core$

The net result of activating your virtualenv is that your PATH variable now points to the tools in `core/bin` and your python will look for libraries in `core/lib`.

Therefore you need to reactivate your virtualenv every time you want to work on your ``core`` environment. 

Install WebCore
^^^^^^^^^^^^^^^
You'll be able to install the latest released version of WebCore via:

.. code-block:: bash

    (core)$ easy_install WebCore WebCore-Start

.. warning:: If you are upgrading from a previous version your command should be:

    .. code-block:: bash

        (core)$ easy_install -U WebCore WebCore-Start

.. note:: In a production environment you probably do not want to install WebCore-Start; simply omit it from this command line.  The WebCore-Start package contains templates used to build new projects.

WebCore and all of its dependencies should download and install themselves.  WebCore offers a few default configurations, if you want the standard group of packages out-of-the-box, you can install using the following command:

.. code-block:: bash

    (core)$ easy_install WebCore[default] WebCore-Start

This will install WebCore and the following packages: Beaker, simplejson, Genshi, and SQLAlchemy.

Deactivating the Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When you are done working simply run the ``deactivate`` virtualenv shell command::

    (core)user@host:~/core$ deactivate 
    user@host:~/core$

This isn't really needed but it's good practice if you want to switch your shell to do some other work.

Installing the Development Version of WebCore
---------------------------------------------

Getting Git
^^^^^^^^^^^

    * All major Linux distributions have this installed. The package is normally named ``git``.
    * On Windows you can download the `Git installer`_

.. _Git installer: http://subversion.tigris.org/getting.html

Getting the Source
^^^^^^^^^^^^^^^^^^

Check out the latest code from the Github repository:

.. code-block:: bash

  (core)$ git clone git://github.com/GothAlice/WebCore.git

Installing the Sources
^^^^^^^^^^^^^^^^^^^^^^

Tell setuptools to use these versions that you have just cloned:

.. code-block:: bash

  (core)$ cd WebCore
  (core)$ python setup.py develop


Validate an Installation
------------------------
To check if you installed WebCore correctly, type

.. code-block:: bash

    (core)$ paster --help

and you should see something like::

    Usage: paster [paster_options] COMMAND [command_options]

    Options:
      --version         show program's version number and exit
      --plugin=PLUGINS  Add a plugin to the list of commands (plugins are Egg
                        specs; will also require() the Egg)
      -h, --help        Show this help message

    Commands:
      create       Create the file layout for a Python distribution
      help         Display help
      make-config  Install a package and create a fresh config file/directory
      points       Show information about entry points
      post         Run a request for the described application
      request      Run a request for the described application
      serve        Serve the described application
      setup-app    Setup an application, given a config file

    WebCore:
      quickstart   Create a new WebCore project.

Notice the "WebCore" command section at the end of the output -- this indicates that WebCore is installed in your current path.