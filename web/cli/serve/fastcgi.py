#!/usr/bin/env python2

"""
  This file is borrowed from django.core.servers.fastcgi

"""
import sys
import os

FASTCGI_HELP = r"""
  Run this project as a fastcgi (or some other protocol supported
  by flup) application. To do this, the flup package from
  http://www.saddi.com/software/flup/ is required.

   runfcgi [options] [fcgi settings]
"""

FASTCGI_OPTIONS = {
    'protocol': 'fcgi',
    'host': None,
    'port': None,
    'socket': None,
    'method': 'fork',
    'daemonize': None,
    'workdir': '/',
    'pidfile': None,
    'maxspare': 5,
    'minspare': 2,
    'maxchildren': 50,
    'maxrequests': 0,
    'debug': None,
    'outlog': None,
    'errlog': None,
    'umask': None,
}

def fastcgi_help(message=None):
    print FASTCGI_HELP
    if message:
        print message
    return False

def runfastcgi(application,**kwargs):
    options = FASTCGI_OPTIONS.copy()
    options.update(kwargs)
    try:
        import flup
    except ImportError, e:
        print >> sys.stderr, "ERROR: %s" % e
        print >> sys.stderr, "  Unable to load the flup package.  In order to run django"
        print >> sys.stderr, "  as a FastCGI application, you will need to get flup from"
        print >> sys.stderr, "  http://www.saddi.com/software/flup/   If you've already"
        print >> sys.stderr, "  installed flup, then make sure you have it in your PYTHONPATH."
        return False

    flup_module = 'server.%s'%options['protocol']
    print flup_module

    if options['method'] in ('prefork', 'fork'):
        wsgi_opts = {
            'maxSpare': int(options["maxspare"]),
            'minSpare': int(options["minspare"]),
            'maxChildren': int(options["maxchildren"]),
            'maxRequests': int(options["maxrequests"]),
        }
        flup_module += '_fork'
    elif options['method'] in ('thread', 'threaded'):
        wsgi_opts = {
            'maxSpare': int(options["maxspare"]),
            'minSpare': int(options["minspare"]),
            'maxThreads': int(options["maxchildren"]),
        }
    else:
        return fastcgi_help("ERROR: Implementation must be one of prefork or thread.")

    wsgi_opts['debug'] = options['debug'] is not None

    try:
        WSGIServer = getattr(__import__('flup.' + flup_module, '', '', flup_module), 'WSGIServer')
    except ImportError:
        print "You need to install flup"
        return False

    if options["host"] and options["port"] and not options["socket"]:
        wsgi_opts['bindAddress'] = (options["host"], int(options["port"]))
    elif options["socket"]:
        wsgi_opts['bindAddress'] = options["socket"]
    elif not options["socket"] and not options["host"] and not options["port"]:
        wsgi_opts['bindAddress'] = None
    else:
        return fastcgi_help("Invalid combination of host, port, socket.")

    if options["daemonize"] is None:
        # Default to daemonizing if we're running on a socket/named pipe.
        daemonize = (wsgi_opts['bindAddress'] is not None)
    else:
        if options["daemonize"]:
            daemonize = True
        else:
            daemonize = False

    daemon_kwargs = {}
    if options['outlog']:
        daemon_kwargs['out_log'] = options['outlog']
    if options['errlog']:
        daemon_kwargs['err_log'] = options['errlog']
    if options['umask']:
        daemon_kwargs['umask'] = int(options['umask'])

    if daemonize:
        from .daemonize import become_daemon
        become_daemon(our_home_dir=options["workdir"], **daemon_kwargs)

    if options["pidfile"]:
        fp = open(options["pidfile"], "w")
        fp.write("%d\n" % os.getpid())
        fp.close()

    WSGIServer(application, **wsgi_opts).run()
