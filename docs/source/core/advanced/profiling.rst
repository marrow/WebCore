******************************
Profiling your Web Application
******************************

.. contents:: Table of Contents


The Repoze Profiler
===================

The ``repoze.profile`` package provides a `WSGI middleware component`_ which aggregates Python profiling data across all requests to a WSGI application. It also provides an HTML UI for viewing profiling data.

This profiling has several restrictions which make it impractical for use during deployment; first, it forces the WSGI server to run with a single thread, second, it impacts performance negatively.

.. _WSGI middleware component: http://svn.repoze.org/repoze.profile/trunk/

To enable repoze profiling of your application, set the following directive in your INI file or as an argument to the ``Application.factory`` method:

.. code-block:: ini

   web.profile = True

The profiler is configurable; the following is a description of these options and their default values:

``web.profile.log`` (default: ``profile.prof``)
   The file in which to store profiling information.

``web.profile.discard`` (default: ``True``)
   Discard the first request. This prevents the overhead of initial imports, class initializations, etc. from effecting the profile results.

``web.profile.flush`` (default: ``True``)
   Flush the profiling information during shutdown. This automatically clears the results so you don't have to.

``web.profile.path`` (default: ``/__profile__``)
   The URL which will display the profiling information graphically. Perform your tests then access this URL for the results.

Performing Tests
----------------

Using ApacheBench
^^^^^^^^^^^^^^^^^

ApacheBench is one of the most popular, and distributed, software packages for stress testing web servers.  Its interface is simple:

.. code-block:: text

   Usage: ab [options] [http[s]://]hostname[:port]/path
   Options are:
       -n requests     Number of requests to perform
       -c concurrency  Number of multiple requests to make
       -t timelimit    Seconds to max. wait for responses
       -b windowsize   Size of TCP send/receive buffer, in bytes
       -p postfile     File containing data to POST. Remember also to set -T
       -T content-type Content-type header for POSTing, eg.
                       'application/x-www-form-urlencoded'
                       Default is 'text/plain'
       -v verbosity    How much troubleshooting info to print
       -w              Print out results in HTML tables
       -i              Use HEAD instead of GET
       -x attributes   String to insert as table attributes
       -y attributes   String to insert as tr attributes
       -z attributes   String to insert as td or th attributes
       -C attribute    Add cookie, eg. 'Apache=1234. (repeatable)
       -H attribute    Add Arbitrary header line, eg. 'Accept-Encoding: gzip'
                       Inserted after all normal header lines. (repeatable)
       -A attribute    Add Basic WWW Authentication, the attributes
                       are a colon separated username and password.
       -P attribute    Add Basic Proxy Authentication, the attributes
                       are a colon separated username and password.
       -X proxy:port   Proxyserver and port number to use
       -V              Print version number and exit
       -k              Use HTTP KeepAlive feature
       -d              Do not show percentiles served table.
       -S              Do not show confidence estimators and warnings.
       -g filename     Output collected data to gnuplot format file.
       -e filename     Output CSV file with percentages served
       -r              Don't exit on socket receive errors.
       -h              Display usage information (this message)
       -Z ciphersuite  Specify SSL/TLS cipher suite (See openssl ciphers)
       -f protocol     Specify SSL/TLS protocol (SSL2, SSL3, TLS1, or ALL)

The easiest way to test GET requests for a URL is as follows:

.. code-block:: bash

   $ ab -n 1001 -c 5 http://127.0.0.1:8080/

Using ApacheBench you can benchmark GET, HEAD, and POST requests, cookies (and thus sessions), and more.


Using Httperf
^^^^^^^^^^^^^

Httperf produces very verbose output and has a lot of options that it doesn't document very well from the command line.  See the `online manual`_ for details.  Quickly, to benchmark your site in a similar fasion to the ApacheBench example above:

.. code-block:: bash

   $ httperf --server 127.0.0.1 --uri / --num-conn 1001 --num-call 1 --rate 5 --timeout 5

.. _online manual: http://www.hpl.hp.com/research/linux/httperf/docs.php
