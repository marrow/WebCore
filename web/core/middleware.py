# encoding: utf-8

"""
"""


import os
import pkg_resources

from paste.deploy.converters import asbool, asint, aslist

import web


__all__ = ['registry', 'middleware', 'template', 'TemplatingMiddleware']
log = __import__('logging').getLogger(__name__)


registry = []



def defaultbool(value, extended=[]):
    if value is True: return True
    
    if isinstance(value, basestring) and str(value).lower() in (['true', 'on', 'yes'] + extended):
        return True
    
    return False


class MiddlewareWrapper(object):
    def __init__(self, func, name, after=None):
        self.func, self.name, self.after = func, name, after
    
    def __repr__(self):
        return "Wrapper(%s, %r) for %r" % (self.name, self.after, self.func)
    
    def __call__(self, *args, **kw):
        return self.func(*args, **kw)


class middleware(object):
    def __init__(self, name, after=None):
        self.name = name
        self.after = after
    
    def __call__(self, func):
        registry.append(
                MiddlewareWrapper(
                        func,
                        self.name,
                        self.after
                    )
            )
        
        return func


@middleware('templating')
def templateinterface(app, config):
    # Automatically use TemplateInterface templating engines unless explicitly forbidden.
    if not defaultbool(config.get('web.templating', True), ['templateinterface']):
        return app
    
    log.debug("Loading TemplateInterface template engine middleware.")
    
    try:
        from cti.middleware import TemplatingMiddleware, registry
        
        registry.append(web.core.namespace)
        
        return TemplatingMiddleware(app, config)
    
    except ImportError: # pragma: no cover
        log.error("TemplateMiddleware not installed; your application is not likely to work.")
        raise


@middleware('widgets', after="templating")
def toscawidgets(app, config):
    if not defaultbool(config.get('web.widgets', False), ['toscawidgets']):
        return app
    
    try:
        from tw.api import make_middleware as ToscaWidgetsMiddleware
        
        twconfig = {
                'toscawidgets.framework': 'webcore',
                'toscawidgets.framework.default_view': config.get('web.templating.engine', 'genshi'),
                'toscawidgets.framework.enable_runtime_checks': config.get('debug', False),
                'toscawidgets.middleware.prefix': config.get('web.widgets.prefix', '/_tw'),
                'toscawidgets.middleware.inject_resources': config.get('web.widgets.inject', True),
                'toscawidgets.middleware.serve_resources': config.get('web.widgets.serve', True)
            }
        
        
        log.debug("Loading ToscaWidgets middleware.")
        return ToscaWidgetsMiddleware(app, twconfig)
    
    except ImportError: # pragma: no cover
        log.warn("ToscaWidgets not installed, widget framework disabled.  You can remove this warning by explicitly defining widgets=False in your config.")


@middleware('authentication', after="widgets")
def webauth(app, config):
    # Use WebAuth (WebCore) authentication and authorization.
    if not defaultbool(config.get('web.auth', False), ['webauth']):
        return app
    
    log.debug("Loading WebAuth middleware.")
    
    from web.auth.middleware import WebAuth
    app = WebAuth(app, config, prefix="web.auth.")
    
    return app
    


@middleware('authentication', after="widgets")
def authkit(app, config):
    # Use AuthKit if requested.
    if not config.get('web.auth', False) == 'authkit':
        config.update({'web.auth.enabled': False})
        return app
    
    try:
        import authkit.authenticate
        
        log.debug("Loading AuthKit middleware.")
        config.update({'web.auth.enabled': True})
        
        app = authkit.authenticate.middleware(app, config, prefix="web.auth.")
        
        return app
    
    except ImportError: # pragma: no cover
        log.warn("AuthKit not installed, authentication and authorization disabled.  Your authorization checks, if any, will fail.")


@middleware('database', after=["widgets", "authentication"])
def database(app, config):
    # Determine if a database engine has been requested, and load the appropriate middleware.
    if not config.get('db.connections', None):
        return app
    
    try:
        for connection in aslist(config.get('db.connections')):
            connection = connection.strip(',')
            
            engine = config.get('db.%s.engine' % (connection, ), 'sqlalchemy')
            
            try:
                if '.' in engine and ':' in engine:
                    engine = web.utils.object.get_dotted_object(engine)
                
                else:
                    engine = pkg_resources.load_entry_point('WebCore', 'webcore.db.engines', engine)
            
            except:
                log.exception("Unable to load engine middleware: %r.", engine)
                raise
            
            try:
                model = config.get('db.%s.model' % (connection, ))
                model = web.utils.object.get_dotted_object(model) if isinstance(model, basestring) else model
            
            except:
                log.exception("Unable to load application model: %r.", model)
                raise
            
            try:
                session = config.get('db.%s.session' % (connection, ), '%s:session' % (config.get('db.%s.model' % (connection, )), ))
                session = web.utils.object.get_dotted_object(session) if isinstance(session, basestring) else session
            
            except:
                log.info("No session defined for the %s database connection.", connection)
            
            app = engine(app, 'db.%s' % (connection, ), model, session, **config)
        
        return app
    
    except:
        log.exception("Database connections not available.")
        raise


@middleware('configuration', after=["sessions", "i18n"])
def configuration(app, config):
    if not defaultbool(config.get('web.config', True), ['paste']):
        return app
    
    from paste.config import ConfigMiddleware
    return ConfigMiddleware(app, config)


@middleware('sessions', after=["authentication", "widgets", "i18n"])
def sessions(app, config):
    if not defaultbool(config.get('web.sessions', False), ['beaker']):
        return app
    
    try:
        from beaker.middleware import SessionMiddleware
        
        beakerconfig = {
                'session.type': "file",
                'session.key': "session"
            }
        
        for i, j in config.iteritems():
            if i.startswith('web.sessions.'):
                beakerconfig['session.' + i[13:]] = j
        
        if 'session.cookie_expires' in beakerconfig and isinstance(beakerconfig['session.cookie_expires'], basestring):
            value = beakerconfig['session.cookie_expires']
            if value.lower() in ['yes', 'on', 'true']:
                beakerconfig['session.cookie_expires'] = True
            elif value.lower() in ['no', 'off', 'false']:
                beakerconfig['session.cookie_expires'] = False
            else:
                # Try to treat it as a number of minutes...
                from datetime import timedelta
                beakerconfig['session.cookie_expires'] = timedelta(minutes=int(value))
        
        log.debug("Loading Beaker session and cache middleware.")
        return SessionMiddleware(app, beakerconfig)
    
    except ImportError: # pragma: no cover
        log.warn("Beaker not installed, sessions disabled.  You can remove this warning by specifying web.sessions = False in your config.")


@middleware('caching', after=["sessions"])
def caching(app, config):
    if not defaultbool(config.get('web.sessions', False), ['beaker']):
        return app
    
    try:
        from beaker.middleware import CacheMiddleware
        
        beakerconfig = {
                'cache.type': "file"
            }
        
        for i, j in config.iteritems():
            if i.startswith('web.cache.'):
                beakerconfig['cache.' + i[10:]] = j
        
        log.debug("Loading Beaker cache middleware.")
        return CacheMiddleware(app, beakerconfig)
    
    except ImportError: # pragma: no cover
        log.warn("Beaker not installed, caching disabled.  You can remove this warning by specifying web.cache = False in your config.")
    


@middleware('debugging', after=["database", "caching", "sessions", "configuration"])
def debugging(app, config):
    if not defaultbool(config.get('web.debug', True), ['weberror']):
        return app
    
    try:
        localconfig = dict(debug=config.get('debug', False))
        
        for i, j in config.iteritems():
            if i.startswith('debug.'):
                localconfig[i[6:]] = j
        
        if asbool(config.get('debug', False)):
            log.debug("Debugging enabled; exceptions raised will display an interactive traceback.")
            
            from weberror.evalexception import EvalException
            return EvalException(app, localconfig)
        
        else:
            log.debug("Debugging disabled; exceptions raised will display a 500 error.")
            
            from weberror.errormiddleware import ErrorMiddleware
            return ErrorMiddleware(app, localconfig)
    
    except ImportError: # pragma: no cover
        log.warn("WebError not installed, interactive exception handling and messaging disabled.  You can remove this warning by specifying web.debugging = False in your config.")


@middleware('registry', after="debugging")
def threadlocal(app, config):
    from paste.registry import RegistryManager
    return RegistryManager(app)


@middleware('static', after="registry")
def static(app, config):
    # Enabled explicitly or while debugging so you can use Paste's HTTP server.
    if config.get('web.static', None) is None and not asbool(config.get('debug', False)):
        return app
    
    if not asbool(config.get('web.static', False)):
        return app
    
    from paste.cascade import Cascade
    from paste.fileapp import DirectoryApp
    
    path = config.get('web.static.path', None)
    
    if path is None:
        # Attempt to discover the path automatically.
        module = __import__(config['web.root'].__module__)
        parts = config['web.root'].__module__.split('.')[1:]
        path = module.__file__
        
        if not parts: parts = ['.']
        
        while parts:
            # Search up the package tree, in case this is an application in a sub-module.
            
            path = os.path.abspath(path)
            path = os.path.dirname(path)
            path = os.path.join(path, 'public')
            
            log.debug("Trying %r", path)
            
            if os.path.isdir(path):
                break
            
            if parts[0] == '.': break
            module = getattr(module, parts.pop(0))
            path = module.__file__
    
    if not os.path.isdir(path):
        log.warn("Unable to find folder to serve static content from.  Please specify web.static.path in your config.")
        return app
    
    log.debug("Serving static files from '%s'.", path)
    
    return Cascade([DirectoryApp(path), app], catch=[401, 403, 404])


@middleware('compression', after="static")
def compression(app, config):
    if not defaultbool(config.get('web.compress', False), ['paste']):
        return app
    
    # Enable compression if requested.
    log.debug("Enabling HTTP compression.")
    
    from paste.gzipper import middleware as GzipMiddleware
    return GzipMiddleware(app, compress_level=asint(config.get('web.compress.level', 6)))


@middleware('profiling', after="compression")
def profiling(app, config):
    if not defaultbool(config.get('web.profile', False), ['repoze']):
        return app
    
    log.debug("Enabling profiling support.")
    
    try:
        from repoze.profile.profiler import AccumulatingProfileMiddleware
    
        return AccumulatingProfileMiddleware(
               app,
               log_filename = config.get('web.profile.log', 'profile.prof'),
               discard_first_request = asbool(config.get('web.profile.discard', 'true')),
               flush_at_shutdown = asbool(config.get('web.profile.flush', 'true')),
               path = config.get('web.profile.path', '/__profile__')
           )
    
    except ImportError: # pragma: no cover
        log.error("Repoze profiling middleware not installed.")
