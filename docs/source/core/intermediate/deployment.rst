**************************
Deploying your Application
**************************

.. contents:: Table of Contents
   :depth: 2
   :local:

.. note:: FastCGI deployment requires the ``flup`` module be installed.



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

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


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
