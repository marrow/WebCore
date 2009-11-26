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







'''
from web.utils.object import DottedFileNameFinder

_engines = dict((_engine.name, _engine) for _engine in pkg_resources.iter_entry_points('python.templating.engines'))
_lookup = web.utils.object.DottedFileNameFinder()


@middleware('templating')
def buffet(app, config):
    # Automatically use Buffet templating engines unless explicitly forbidden.
    if not defaultbool(config.get('web.templating', False), ['buffet']):
        return app
    
    log.debug("Loading Buffet template engine middleware.")
    return TemplatingMiddleware(app, config)


class DottedFileNameFinder(object):
    """this class implements a cache system above the
    get_dotted_filename function and is designed to be stuffed
    inside the app_globals.

    It exposes a method named get_dotted_filename with the exact
    same signature as the function of the same name in this module.

    The reason is that is uses this function itself and just adds
    caching mechanism on top.
    """
    def __init__(self):
        self.__cache = dict()

    def get_dotted_filename(self, template_name, template_extension='.html'):
        """this helper function is designed to search a template or any other
        file by python module name.

        Given a string containing the file/template name passed to the @expose
        decorator we will return a resource useable as a filename even
        if the file is in fact inside a zipped egg.

        The actual implementation is a revamp of the Genshi buffet support
        plugin, but could be used with any kind a file inside a python package.

        @param template_name: the string representation of the template name
        as it has been given by the user on his @expose decorator.
        Basically this will be a string in the form of:
        "genshi:myapp.templates.somename"
        @type template_name: string

        @param template_extension: the extension we excpect the template to have,
        this MUST be the full extension as returned by the os.path.splitext
        function. This means it should contain the dot. ie: '.html'

        This argument is optional and the default value if nothing is provided will
        be '.html'
        @type template_extension: string
        """
        try:
            return self.__cache[template_name]

        except KeyError:
            # the template name was not found in our cache
            divider = template_name.rfind('.')
            if divider >= 0:
                package = template_name[:divider]
                basename = template_name[divider + 1:] + template_extension
                result = resource_filename(package, basename)

            else:
                result = template_name

            self.__cache[template_name] = result

            return result
            

def template(template, **extras):
    def outer(func):
        def inner(*args, **kw):
            return TemplatingMiddleware.render(template, func(*args, **kw), **extras)
        
        # Become more transparent.
        inner.__name__ = func.__name__
        inner.__doc__ = func.__doc__
        inner.__dict__ = func.__dict__
        inner.__module__ = func.__module__
        
        return inner
    return outer


class TemplatingMiddleware(object):
    def __init__(self, application, config=dict(), **kw):
        self.config = config.copy()
        self.config.update(kw)
        self.application = application
    
    @classmethod
    def variables(cls):
        def lookup(template_name, template_extension='.html'):
            return _lookup.get_dotted_filename(template_name, template_extension)
        
        return dict(
                web=web.utils.dictionary.adict(
                        request = web.core.request,
                        response = web.core.response,
                        session = web.core.session
                    ),
                lookup = lookup,
            )
    
    @classmethod
    def render(cls, template, data, **kw):
        # Determine the templating engine to use.
        # The template engine can be defined by, in order of presidence, the returned value, the environment, or the configuration.
        if ':' in template: template = template.split(':')
        engine = template[0] if isinstance(template, list) else web.core.request.environ.get("buffet.engine", "genshi")
        template = template[1] if isinstance(template, list) else template
        
        # Allocate a Buffet engine to handle this template request.
        # TODO: Cache the result of this based on the input of variable callback and options.
        
        options = web.core.request.environ.get("buffet.options", dict())
        options.update(kw)
        
        if 'buffet.format' in options: del options['buffet.format']
        if 'buffet.fragment' in options: del options['buffet.fragment']
        
        if template == 'json':
            try:
                from json import dumps
            except ImportError:
                from simplejson import dumps
            
            web.core.response.content_type = 'application/json; charset=utf-8'
            return dumps(data, **options)
        
        elif template == 'bencode':
            from web.extras.bencode import EnhancedBencode
            engine = EnhancedBencode()
            
            web.core.response.content_type = 'application/x-bencode; charset=utf-8'
            return engine.encode(data)
        
        engine = _engines[engine].load()
        engine = engine(cls.variables, options)
        
        del options
        
        return engine.render(
                data,
                kw.get("buffet.format", web.core.request.environ.get("buffet.format", "html")),
                kw.get("buffet.fragment", web.core.request.environ.get("buffet.fragment", False)),
                template
            )
    
    def __call__(self, environ, start_response):
        environ.update({
                'buffet.engine': self.config.get("buffet.engine", "genshi"),
                'buffet.options': self.config.get("buffet.options", dict()),
                'buffet.format': self.config.get("buffet.format", "html"),
                'buffet.fragment': self.config.get("buffet.fragment", False),
            })
        
        result = self.application(environ, start_response)
        
        # Bail if the returned value is not a tuple.
        if not isinstance(result, tuple):
            return result
        
        if len(result) == 2: template, data, extras = result + (dict(), )
        elif len(result) == 3: template, data, extras = result
        
        if not isinstance(template, str) or not isinstance(data, dict) or not isinstance(extras, dict):
            raise TypeError("Invalid tuple values returned to TemplatingMiddleware.")
        
        result = self.render(template, data, **extras)
        
        if isinstance(result, str):
            log.debug("Received string response.")
            web.core.response.body = result
        
        elif isinstance(result, unicode):
            log.debug("Received unicode response.")
            web.core.response.unicode_body = result
        
        return web.core.response(environ, start_response)
'''