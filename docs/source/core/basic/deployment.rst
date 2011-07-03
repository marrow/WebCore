**************************
Deploying your Application
**************************

.. contents:: Table of Contents
   :depth: 2
   :local:

.. note:: FastCGI deployment requires the ``flup`` module be installed.



General Web App Configuration
=============================

If you are going to use your application to cover a whole domain, then you can
just skip ahead.  If you are going to mount your application as a sub-folder,
you'll need to adjust the production INI file to include an additional section
and add an extra line below the `use` line in the `[app:main]` section
regardless of which method you use to deploy (**except** mod_wsgi).

.. code-block:: ini

   [app:main]
   use = egg:WebCore
   filter-with = proxy-prefix
   
   # ...
   
   [filter:proxy-prefix]
   use = egg:PasteDeploy#prefix
   prefix = /path/to/app/on/site



Nginx
=====

We like Nginx.  It's fast, incredibly memory-efficient, and fairly easy to use.  Using Nginx you have a number of deployment options.


FastCGI
-------

Web Application Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Update your deployment INI file's ``[server:main]`` section, replacing the ``use``, ``host``, and ``port`` directives.  Also ensure that ``debug`` and ``web.static`` are set to ``False`` in your ``[app:main]`` section.

.. code-block:: ini

   use = egg:PasteScript#flup_fcgi_thread
   socket = /home/amcgregor/var/run/cms.sock
   umask = 0

If you want to treat your INI file as an executable script, you can add an ``[exe]`` section like this:

.. code-block:: ini

   [exe]
   command = serve
   daemon = true

   pid-file = /home/amcgregor/var/run/cms.pid
   log-file = /home/amcgregor/var/log/cms.log

Update the paths as necessary.  Mark the script as executable using ``chmod 755 <inifile>`` and running it will start the application server.  You can stop the application server by running your INI file with the ``--stop-daemon`` switch.

Nginx Configuration
^^^^^^^^^^^^^^^^^^^

.. code-block:: nginx

   server {
       server_name                     www.gothcandy.com gothcandy.com;
       listen                          80;

       access_log                      /home/amcgregor/var/log/gothcandy-access.log combined;
       error_log                       /home/amcgregor/var/log/gothcandy-error.log error;

       charset                         off;
       location ~ /\.ht                { deny all; }
       location ~ \.flv$               { flv; }
       location ~ /favicon\.ico        { error_log none; }
       location ~ /robots\.txt         { error_log none; }

       location / {
           root                        /home/amcgregor/app/site/src/gothcandy/public;

           include                     core/fcgi.conf;
           fastcgi_param               SCRIPT_NAME "";

           if ( !-e $request_filename ) {
               break;
           }
           
           fastcgi_pass                unix:/home/amcgregor/var/run/cms.sock;
       }
   }

Set the paths according to your application; you will need to update the ``access_log``, ``error_log``, ``root``, and ``fastcgi_pass`` lines.  This configuration will serve static files directly from Nginx.
   


Load Balanced Proxy
-------------------

Web Application Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change your INI file's ``port`` directive (in the ``[server:main]`` section) to a port number unused by other applications on the production server.  Also change the ``host`` directive to allow only localhost connections by entering ``127.0.0.1``.


Nginx Configuration
^^^^^^^^^^^^^^^^^^^

.. code-block:: nginx

   upstream webcore {
       server localhost:8080;
   }
   
   server {
       server_name                     www.gothcandy.com gothcandy.com;
       listen                          80;

       access_log                      /home/amcgregor/var/log/gothcandy-access.log combined;
       error_log                       /home/amcgregor/var/log/gothcandy-error.log error;

       charset                         off;
       location ~ /\.ht                { deny all; }
       location ~ \.flv$               { flv; }
       location ~ /favicon\.ico        { error_log none; }
       location ~ /robots\.txt         { error_log none; }

       location / {
           root                        /home/amcgregor/app/site/src/gothcandy/public;

           if ( -e $request_filename ) {
               break;
           }
           
           proxy_pass                  http://webcore;
       }
   }

Set the port and paths according to your application; you will need to update the ``server``, ``access_log``, ``error_log``, and ``root`` lines.  This configuration will serve static files directly from Nginx.

If you create additional copies of the deployment INI file with different port numbers, you can add them to the webcore proxy list.  It is not advisable to create more running services than there are CPU cores.



Apache
======

mod_wsgi
--------

This is the recommended way to deploy applications on Apache2. Make sure you
have the **mod_wsgi** module loaded. It is recommended that you run it in
daemon mode to easily enable reloading your applications. Installation and
configuration instructions can be found on the
`mod_wsgi website <http://code.google.com/p/modwsgi/wiki/InstallationInstructions>`_.

Deployment with mod_wsgi requires a "WSGI stub" file, which is a Python script
that initializes the application. When the application is accessed for the
first time, mod_wsgi executes the stub file and looks for the ``application``
variable which should be a standard WSGI conforming callable. The following
example configuration assumes the following:

* You are deploying under the public-facing path ``/customer/myapp/``
* The filesystem root for your project is ``/var/www/customer/myapp/``
* Your application's static files are at ``/var/www/customer/myapp/static/``
* Apache's document root is set at ``/var/www/``

First, copy your application to /var/www/customer/myapp/ if it's not already
there. Suppose your application's top level package name is ``funkyproject``.
The package's directory would then be ``/var/www/customer/myapp/funkyproject/``.

When your application is installed, set up a
`virtualenv <http://www.virtualenv.org/en/latest/#what-it-does>`_:

.. code-block:: sh

    $ cd /var/www/customer/myapp
    $ virtualenv --distribute --no-site-packages virtualenv

Then the application should be made available in the virtualenv:

.. code-block:: sh

    $ python setup.py develop

Then, create the WSGI stub file at ``/var/www/customer/myapp/application.wsgi``:

.. code-block:: python

    import os.path
    import logging.config

    # Activate the virtual environment
    here = os.path.dirname(__file__)
    activate = os.path.join(here, 'virtualenv', 'bin', 'activate_this.py')
    execfile(activate, dict(__file__=activate))

    # Set up logging
    inifile = os.path.join(here, 'production.ini')
    logfile = os.path.join(here, 'application.log')
    logging.config.fileConfig(inifile, dict(logfile=logfile))

    # Load the application
    from paste.deploy import loadapp
    application = loadapp('config:%s' % inifile)

Finally, add this configuration to your Apache virtualhost:

.. code-block:: apache

    # General configuration
    WSGIDaemonProcess wsgiapp user=myname group=mygroup display-name=%{GROUP}
    WSGIProcessGroup wsgiapp

    # Per-application configuration
    WSGIScriptAlias /customer/myapp /var/www/customer/myapp/application.wsgi
    AliasMatch /customer/myapp/([^_].*?\.[a-z0-9]+)$ /var/www/customer/myapp/static/$1

This configuration routes all requests under /customer/myapp to your application,
**except** ones whose names end with a dot and some suffix and ones starting
with an underscore. The former exception is so that Apache can serve static
files directly without invoking your application. The latter is necessary for
some resource injecting middleware (such as WebError) to work properly.

Now just reload your Apache configuration and you're set. If you update your
application code, you can reload the application by either killing the relevant
mod_wsgi daemon process or touching the WSGI script, depending on how you
configured mod_wsgi.

.. note:: 
    With mod_wsgi it is **not** necessary to use PrefixMiddleware, because mod_wsgi
    sets up the SCRIPT_NAME and PATH_INFO variables properly relative to the
    application root.


mod_proxy
---------

This is not the recommended method of deployment when using Apache.  This method effectively runs the development Paste HTTP server and has Apache proxy requests, thus this method possibly suffers a performance penalty.  Additionally, using `mod_proxy` requires that you manage the runtime environment (starting and stopping as per a service) manually.  It happens to be the easiest method for deployment, requiring only the common `mod_proxy` module, though.

Application Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

Your production INI file should define a port to serve requests through that does not conflict with other services.  Some hosting providers will allocate you a range or specific port numbers that you can use.  You should also ensure your web app will only listen to connections from the local server, not requests over the internet.

Apache Configuration
^^^^^^^^^^^^^^^^^^^^

Ensure Apache is configured to load `mod_proxy` and related modules.  Look for lines like the following, which may be commented out, and ensure they are *not* commented out.

.. code-block:: apache

   LoadModule proxy_module modules/mod_proxy.so
   LoadModule proxy_connect_module modules/mod_proxy_connect.so
   LoadModule proxy_http_module modules/mod_proxy_http.so
   LoadModule proxy_balancer_module modules/mod_proxy_balancer.so

Configure Apache to listen to virtual host requests and define a new virtual host.  In a light-weight setup this may be done from within the `httpd.conf` file, or may be delegated out to an external file like `httpd-vhosts.conf` or even a folder with one file per virtual host.

.. code-block:: apache

   <VirtualHost *>
       ServerName mytgapp.blabla.com
       ServerAdmin here-your-name@blabla.com
       #DocumentRoot /srv/www/vhosts/mytgapp
       Errorlog /var/log/apache2/mytgapp-error_log
       Customlog /var/log/apache2/mytgapp-access_log common
       UseCanonicalName Off
       ServerSignature Off
       AddDefaultCharset utf-8
       ProxyPreserveHost On
       ProxyRequests Off
       ProxyPass /error/ !
       ProxyPass /icons/ !
       ProxyPass /favicon.ico !
       #ProxyPass /static/ !
       ProxyPass / http://127.0.0.1:8080/
       ProxyPassReverse / http://127.0.0.1:8080/
   </VirtualHost>
