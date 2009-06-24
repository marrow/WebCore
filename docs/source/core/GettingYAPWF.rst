Installing YAPWF
================

This document provides several methods of installing YAPWF; the method you choose will depend on your level of experience and platform.

We recommend installing YAPWF into a virtual environment which will prevent any interference with your system's installed packages and won't unknowingly upgrade any Python libraries that your system needs.

If you want to build packages of YAPWF for your system please send an email to yapwf-devel@yapwf.org.

Prerequisites for all methods
-----------------------------

  1. Python 2.5
  2. Setuptools
  3. virtualenv
  4. Application dependancies

Python
~~~~~~

YAPWF works with any version of python between 2.5 and 2.6. The most widely deployed version of python at the moment of this writing is version 2.5.  Python 2.6 will require additional steps which will be covered in the appropriate sections.  Python 3.0 is currently unsupported due to lack of support in many of our upstream packages.

We recommend you use your system's default Python install or follow the instructions provided here: http://python.org/download/

If you don't know which version of python you have installed you can find out with the following command:

.. code-block:: bash

   $ python --version
   Python 2.5.2

Installing setuptools
~~~~~~~~~~~~~~~~~~~~~

On Windows
""""""""""

Download http://peak.telecommunity.com/dist/ez_setup.py and then run it from the command line.

On Unix
"""""""

.. code-block:: bash

    $ wget http://peak.telecommunity.com/dist/ez_setup.py | sudo python

You may also use your system's package for setuptools, for example, on Gentoo:

.. code-block:: bash

    $ emerge -av setuptools

On Unix (non-root)
""""""""""""""""""

TODO

Post Install
""""""""""""

You most likely want setuptools 0.6c9 or greater as this one provides fixes to work with svn1.5.  If you ever get an error regarding 'log' please run:

.. code-block:: bash

    $ easy_install -U setuptools

To confirm this worked run:
   
.. code-block:: bash

    $ python -c "print __import__('setuptools').__version__"
    0.6c9

Installing Database and Drivers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. hint::
    The installation of the database back-end is a topic outside of the scope of this document.

YAPWF uses SQLAlchemy as its default ORM (Object Relational Mapper) layer, although a number of database libraries are supported.  SQLAlchemy maintains excellent documentation on all the `engines supported`_.

.. _engines supported: http://www.sqlalchemy.org/docs/05/reference/dialects/index.html

Cygwin users can't use sqlite as it does not include the necessary binary file (``sqlite3.dll``).  If you want to run Cygwin you'll need to install a different database.

Installing non-Python Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will most likely need a C compiler and the Python header files. Please see the appropriate section below.

Windows
"""""""
We include pre-compiled binaries for windows in our package index.

If you want to help us keep all binaries up to date please write to yapwf-devel@yapwf.org to become part of our Windows egg building team.

You may also want the `win32api`_ package as it provides some very useful tools for Windows developers, the first you will encounter is the ability to make virtualenv work with paths that contain spaces.

.. _win32api: http://starship.python.net/crew/mhammond/win32/

See also pylunch.

See also windows installer.

Cygwin
""""""
You must perform all operations, including setup operations, within DOS command windows, not Cygwin command window.

MacOS
""""""
Xcode is required to build some binary dependancies and is available on the OS X CD or at http://developer.apple.com/tools/xcode/.

Debian, Ubuntu 
""""""""""""""
Debian derived Linux versions require ``python-dev`` and ``build-essential``::

    $ apt-get install python-dev
    $ apt-get install build-essential

RedHat, Fedora, CentOS
"""""""""""""""""""""""
Fedora users will need the ``python-devel`` rpm::

    $ yum install python-devel

Gentoo
""""""
Nothing extra is required as Gentoo has a full development environment configured by default.

Other Linux and UNIX
""""""""""""""""""""
You'll need a working version of the GCC compiler installed, as well as the Python headers.  

Installing Virtualenv
~~~~~~~~~~~~~~~~~~~~~
We strongly advise you to install all your YAPWF apps inside a virtualenv.  If you ask for support without a virtualenv to isolate your packages we will usually ask you to go get virtualenv before proceeding further.

``virtualenv`` is a tool that you can use to keep your Python path clean and tidy.  It allows you to install new packages and all of their dependencies into a clean working environment, thus eliminating the possibility that installing YAPWF or some other new package will break your existing Python environment.

The other great advantage of virtualenv is that it allows you to run multiple versions of the same package in parallel which is great for running both the production version and the development version of an application on the same machine.

People with a systems administration background could consider virtualenv as a variation of an OS jail (chroot) which is also good for security as your installation is totally isolated. This makes virtualenv great for deploying production sites.

installing ``virtualenv``:

On Windows::

    easy_install virtualenv

On Unix:

.. code-block:: bash

    $ sudo easy_install virtualenv

On Unix (non-root):

.. code-block:: bash

    $ easy_install --install-dir=$HOME/lib/python2.5/ --script-dir=$HOME/bin/ virtualenv

will output something like:

.. code-block:: text

    Searching for virtualenv
    Reading http://pypi.python.org/simple/virtualenv/
    Best match: virtualenv 1.3.2
    Downloading http://pypi.python.org/packages/2.5/v/virtualenv/virtualenv-1.3.2-py2.5.egg#md5=1db8cdd823739c79330a138327239551
    Processing virtualenv-1.3.2-py2.5.egg
    .....
    Processing dependencies for virtualenv
    Finished processing dependencies for virtualenv

Installing YAPWF
----------------

We provide several methods for installing YAPWF which depend on the level of control you want over it:

    1. plain virtualenv
    2. development version

.. hint::
    Please note we are using ``yapwf`` as the name of the virtual environment.  This is simply a convention in our documentation, the name of the virtualenv depends totally on the user and should be named according to the project it contains.

Basic Installation
~~~~~~~~~~~~~~~~~~

First, ``cd`` to the directory where you want your virtual environment for YAPWF. Note the virtualenv will be created as a subdirectory here.

Now create a new virtual environment named ``yapwf``:

.. code-block:: bash

    $ virtualenv --no-site-packages yapwf

that produces something like this::

     Using real prefix '/usr/local'
     New python executable in yapwf/bin/python
     Installing setuptools............done.

.. _activate_virtualenv:

Activate your virtualenv 
""""""""""""""""""""""""
First go inside the virtualenv::

    $ cd yapwf

On Windows you activate a virtualenv with the command::

    Scripts\activate.bat

On Unix you activate a virtualenv with the command:

.. code-block:: bash

    $ . bin/activate

If you are on Unix your prompt should change to indicate that you're in a virtualenv.
It will look something like this::

    (yapwf)username@host:~/yapwf$

The net result of activating your virtualenv is that your PATH variable now points to the tools in `yapwf/bin` and your python will look for libraries in `yapwf/lib`.

Therefore you need to reactivate your virtualenv every time you want to work on your ``yapwf`` environment. 

Install YAPWF
"""""""""""""
You'll be able to install the latest released version of YAPWF via:

.. code-block:: bash

    (yapwf)$ easy_install YAPWF

.. warning :: if you are upgrading from a previous version your command should be:

    .. code-block:: bash

        (tg2env)$ easy_install -U YAPWF

YAPWF and all of its dependencies should download and install themselves.  YAPWF offers a few default configurations, if you want the standard group of packages out-of-the-box, you can install YAPWF using the following:

.. code-block:: bash

    (yapwf)$ easy_install YAPWF[default]

This will install YAPWF and the following packages: Beaker, simplejson, Genshi, and SQLAlchemy.

Deactivating the Environment
""""""""""""""""""""""""""""
When you are done working simply run the ``deactivate`` virtualenv shell command::

    (yapwf)user@host:~/yapwf$ deactivate 
    user@host:~/yapwf$

This isn't really needed but it's good practice if you want to switch your shell to do some other work.

Installing the Development Version of Turbogears 2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Getting Git
"""""""""""

    * All major Linux distributions have this installed. The package is normally named ``git``.
    * On Windows you can download the `Git installer`_

.. _Git installer: http://subversion.tigris.org/getting.html

Getting the Source
""""""""""""""""""

Check out the latest code from the Github repository:

.. code-block:: bash

  (yapwf)$ git clone git://github.com/GothAlice/YAPWF.git

Installing the Sources
""""""""""""""""""""""

Tell setuptools to use these versions that you have just cloned:

.. code-block:: bash

  (yapwf)$ cd YAPWF
  (yapwf)$ python setup.py develop

Validate the Installation
-------------------------
To check if you installed YAPWF correctly, type

.. code-block:: bash

    (tg2env)$ paster --help

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

    YAPWF:
      quickstart   Create a new YAPWF project.

Notice the "YAPWF" command section at the end of the output -- this indicates that YAPWF is installed in your current path.

What's next?
============
If you are new to YAPWF you will want to continue with the `Quick Start Guide <NewProject.html>`_

.. If you are a TG1 user be sure to check out our `What's new in TurboGears 2.0 <WhatsNew.html>`_ page to get a picture of what's changed in TurboGears2 so far.