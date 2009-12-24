**************************
Deploying your Application
**************************

.. contents:: Table of Contents
   :depth: 2
   :local:

.. note:: FastCGI deployment requires the ``flup`` module be installed.



General Web App Configuration
=============================

If you are going to use your application to cover a whole domain, then you can just skip ahead.  If you are going to mount your application as a sub-folder, you'll need to adjust the production INI file to include an additional section and add an extra line below the `use` line in the `[app:main]` section regardless of which method you use to deploy.

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

mod_proxy
---------

This is not the recommended method of deployment when using Apache.  This method effectively runs the development Paste HTTP server and has Apache proxy requests, thus this method possibly suffers a performance penalty.  Additionally, using `mod_proxy` requires that you manage the runtime environment (starting and stopping as per a service) manually.  It happens to be the easiest method for deployment, requiring only the common `mod_proxy` module, though.

Application Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

Your production INI file should define a port to serve requests through that does not conflict with other services.  Some hosting providers will allocate you a range or specific port numbers that you can use.  You should also ensure your web app will only listen to connections from the local server, not requests over the internet.

Apache Configuration
^^^^^^^^^^^^^^^^^^^^

Ensure Apache is configured to load `mod_proxy` and related modules.  Look for lines like the following, which may be commented out, and ensure they are *not* commented out.

.. code-block: apache

   LoadModule proxy_module modules/mod_proxy.so
   LoadModule proxy_connect_module modules/mod_proxy_connect.so
   LoadModule proxy_http_module modules/mod_proxy_http.so
   LoadModule proxy_balancer_module modules/mod_proxy_balancer.so

Configure Apache to listen to virtual host requests and define a new virtual host.  In a light-weight setup this may be done from within the `httpd.conf` file, or may be delegated out to an external file like `httpd-vhosts.conf` or even a folder with one file per virtual host.




mod_wsgi
--------

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


Lighttpd
========

FastCGI
-------

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


HTTP Proxy
----------

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
