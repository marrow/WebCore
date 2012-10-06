# encoding: utf-8

import urllib
import web

from marrow.util.bunch import Bunch
from marrow.util.convert import boolean, array
from marrow.util.object import load_object


__all__ = ['WebAuth', 'BasicAuthMiddleware']
log = __import__('logging').getLogger(__name__)

default_config = Bunch(
        name='uid',
        intercept='403',
        handler='/login',
        internal=False,
        lookup=None,
        authenticate=None
    )


class WebAuth(object):
    def __init__(self, application, config=dict(), prefix='auth.'):
        self.application = application

        prefix_length = len(prefix)
        our_config = Bunch(default_config.copy())

        for i, j in config.iteritems():
            if i.startswith(prefix):
                our_config[i[prefix_length:]] = j

        our_config.intercept = [i.strip() for i in array(our_config.intercept)]
        our_config.internal = boolean(our_config.internal)

        if our_config.lookup is None:
            raise Exception('You must define an authentication lookup method.')

        our_config.lookup = self.get_method(our_config.lookup)
        our_config.authenticate = self.get_method(our_config.authenticate)

        web.auth.config = our_config

    def get_method(self, string):
        """Returns a lazily-evaluated callable."""

        if not string:
            return None

        if hasattr(string, '__call__'):
            return string

        package, reference = string.split(':', 1)
        prop = None

        if '.' in reference:
            reference, prop = reference.rsplit('.', 1)

        obj = load_object('%s:%s' % (package, reference))

        if not prop:
            def lazy(*args, **kw):
                return obj(*args, **kw)

            return lazy

        def lazy(*args, **kw):
            return getattr(obj, prop)(*args, **kw)

        return lazy

    def authenticate(self, environ, start_response):
        raise web.core.http.HTTPTemporaryRedirect(location=\
                web.auth.config.handler + '?redirect=' + \
                urllib.quote_plus(environ['SCRIPT_NAME']) + \
                urllib.quote_plus(environ['PATH_INFO'])
            )

    def __call__(self, environ, start_response):
        session = environ['beaker.session']
        config = web.auth.config

        # We set this to None on the first request to ensure the session ID stabalizes.
        if config.name not in session:
            session[config.name] = None
            session.save()

        if 'paste.registry' in environ:
            environ['paste.registry'].register(
                    web.auth.user,
                    config.lookup(session[config.name]) if session[config.name] else None
                )

        def our_start_response(status, headers):
            if status.split(' ', 1)[0] in config.intercept:
                return self.authenticate(environ, start_response)

            return start_response(status, headers)

        try:
            result = self.application(environ, our_start_response)
        except web.core.http.HTTPException, e:
            return e(environ, start_response)

        return result
