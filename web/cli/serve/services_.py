# -*- coding: utf-8 -*-
"""
    flaskext.actions.server_actions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import sys,os
from werkzeug import script

def runfcgi(application, before_daemon=None):
    def action( 
            protocol            =   'fcgi',
            hostname            =   ('h', ''),
            port                =   ('p', 3001),
            socket              =   '',
            method              =   'threaded',
            daemonize           =   False,
            workdir             =   '.',
            pidfile             =   '',
            maxspare            =    5,
            minspare            =    2,
            maxchildren          =    50,
            maxrequests         =    0,
            debug               =    False,
            outlog              =   '/dev/null',
            errlog              =   '/dev/null',
            umask               =   022,
        ):
        """run application use flup
        you can choose these arguments:
        protocol :   scgi, fcgi or ajp
        method   :   threaded or fork
        socket   :   Unix domain socket
        children :   number of threads or processes"""
        from .fastcgi import runfastcgi
        runfastcgi(
            application         =  application,
            protocol            =  protocol,
            host                =  hostname,
            port                =  port,
            socket              =  socket,
            method              =  method,
            daemonize           =  daemonize,
            workdir             =  workdir,
            pidfile             =  pidfile,
            maxspare            =  maxspare,
            minspare            =  minspare,
            maxchildren         =  maxchildren,
            maxrequests         =  maxrequests,
            debug               =  debug,
            outlog              =  outlog,
            errlog              =  errlog,
            umask               =  umask,
                )

    return action

def run_twisted_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use twisted http server
        """
        from twisted.web import server, wsgi
        from twisted.python.threadpool import ThreadPool
        from twisted.internet import reactor
        thread_pool = ThreadPool()
        thread_pool.start()
        reactor.addSystemEventTrigger('after', 'shutdown', thread_pool.stop)
        factory = server.Site(wsgi.WSGIResource(reactor, thread_pool, app))
        reactor.listenTCP(int(port), factory, interface=self.host)
        reactor.run()

    return action

def run_appengine_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use appengine http server
        """
        from google.appengine.ext.webapp import util
        util.run_wsgi_app(app)
    return action

def run_gunicorn_server(app):
    def action(bind=('b','127.0.0.1:8000'),workers=('w',4),pid=('p','tmp/flask.pid'),log_file='tmp/flask.log',log_level='info'):
        """run application use gunicorn http server
        """
        from gunicorn import version_info
        if version_info < (0, 9, 0):
            from gunicorn.arbiter import Arbiter
            from gunicorn.config import Config
            arbiter = Arbiter(Config({'bind':bind,'workers': workers,'pidfile':pidfile,'logfile':logfile}), app)
            arbiter.run()
        else:
            from gunicorn.app.base import Application

            class FlaskApplication(Application):
                def init(self, parser, opts, args):
                    return {
                        'bind': bind,
                        'workers': workers,
                        'pidfile':pid,
                        'logfile':log_file,
                        'loglevel':log_level,
                    }

                def load(self):
                    return app

            FlaskApplication().run()
    return action

def run_tornado_server(app):
    """run application use tornado http server
    """
    def action(port=('p', 8000)):
        import tornado.wsgi
        import tornado.httpserver
        import tornado.ioloop
        container = tornado.wsgi.WSGIContainer(app)
        server = tornado.httpserver.HTTPServer(container)
        server.listen(port=port)
        tornado.ioloop.IOLoop.instance().start()
    return action

def run_fapws_server(app):
    def action(host=('h','127.0.0.1'),port=('p', '8000')):
        """run application use fapws http server
        """
        import fapws._evwsgi as evwsgi
        from fapws import base
        evwsgi.start(host, port)
        evwsgi.set_base_module(base)
        evwsgi.wsgi_cb(('', app))
        evwsgi.run()
    return action

def run_meinheld_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use Meinheld http server
        """
        from meinheld import server
        server.listen((host, port))
        server.run(app)
    return action

def run_cherrypy_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use CherryPy http server
        """
        from cherrypy import wsgiserver
        server = wsgiserver.CherryPyWSGIServer((host, port), app)
        server.start()
    return action

def run_paste_server(app):
    def action(host=('h','127.0.0.1'),port=('p', '8000')):
        """run application use Paste http server
        """
        from paste import httpserver
        httpserver.serve(app, host=host, port=port)
    return action

def run_diesel_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use diesel http server
        """
        from diesel.protocols.wsgi import WSGIApplication
        application = WSGIApplication(app, port=self.port)
        application.run()
    return action

def run_gevent_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use gevent http server
        """
        from gevent import wsgi
        wsgi.WSGIServer((host, port), app).serve_forever()
    return action

def run_eventlet_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use eventlet http server
        """
        from eventlet import wsgi, listen
        wsgi.server(listen((host, port)), app)
    return action

def run_eurasia_server(app):
    def action(hostname=('h', '0.0.0.0'), port=('p', 8000)):
        """run application use eurasia http server"""
        try:
            from eurasia import WSGIServer
        except ImportError:
            print "You need to install eurasia"
            sys.exit()
        server = WSGIServer(app, bindAddress=(hostname, port))
        server.run()
    return action

def run_rocket_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use rocket http server
        """
        from rocket import Rocket
        server = Rocket((host, port), 'wsgi', { 'wsgi_app' : app })
        server.start()
    return action


server_actionnames = {
        'runfcgi':runfcgi,
        'runtwisted':run_twisted_server,
        'run_appengine':run_appengine_server,
        'run_gevent':run_gevent_server,
        'run_eventlet':run_eventlet_server,
        'run_gunicorn':run_gunicorn_server,
        'run_rocket':run_rocket_server,
        'run_eurasia':run_eurasia_server,
        'run_tornado':run_tornado_server,
        'run_fapws':run_fapws_server,
        'run_meinheld':run_meinheld_server,
        'run_cherrypy':run_cherrypy_server,
        'run_paste_server':run_paste_server,
        'run_diesel':run_diesel_server,
        }


