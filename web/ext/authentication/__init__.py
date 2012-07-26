# encoding: utf-8
from __future__ import division, print_function, absolute_import

from functools import partial, wraps
from base64 import b64decode

from marrow.util.compat import basestring, unicode, bytes
from marrow.wsgi.exceptions import HTTPUnauthorized, HTTPBadRequest, HTTPForbidden, HTTPTemporaryRedirect


class AuthenticationExtension(object):
    uses = ('session', 'template', 'database')
    provides = ('authentication',)

    def __init__(self, context, **default_options):
        super(AuthenticationExtension, self).__init__()

        default_options.setdefault('method', 'session')
        default_options.setdefault('realm', 'WebCore application')
        default_options.setdefault('sessionkey', '__user_id')
        self.default_options = default_options

        self._validate_options(default_options)
        if default_options['method'] == 'session':
            self.needs = ['session']

    @staticmethod
    def _validate_options(options):
        if options['method'] not in ('basic', 'session'):
            raise ValueError('Invalid value for option "method": %s' % options['method'])

        if not 'auth_callback' in options:
            raise ValueError('Missing required option: auth_callback')
        auth_callback = options['auth_callback']
        if not callable(auth_callback):
            raise ValueError('Option "auth_callback" must be a callable, got %r instead' % type(auth_callback))

        if options['method'] == 'session':
            if 'lookup_callback' not in options:
                raise ValueError('Missing required option: lookup_callback')
            lookup_callback = options['lookup_callback']
            if not callable(lookup_callback):
                raise ValueError('Option "lookup_callback" must be a callable, got %r instead' % type(lookup_callback))

        realm = options.get('realm')
        if isinstance(realm, unicode):
            realm = realm.encode('iso-8859-1')
        elif not isinstance(realm, bytes):
            raise ValueError('Option "realm" must be a string, got %r instead' % type(realm))

        sessionkey = options.get('sessionkey')
        if not isinstance(sessionkey, basestring):
            raise TypeError('Option "sessionkey" must be a string, got %r instead' % type(sessionkey))

    def start(self, context):
        context.user = None
        context.log = context.log.data(user=None)
        if hasattr(context, 'namespace'):
            context.namespace.user = None

    def prepare(self, context):
        context.authenticate = partial(self.authenticate, context)
        context.deauthenticate = partial(self.deauthenticate, context)
        context._authentication_options = self.default_options.copy()

    def dispatch(self, context, consumed, handler, is_endpoint):
        if hasattr(handler, '__auth__'):
            context._authentication_options.update(handler.__auth__)
            self._validate_options(context._authentication_options)

        if is_endpoint:
            # Determine the credentials to authenticate with, based on the configured method
            options = context._authentication_options
            if options['method'] == 'basic':
                if not 'HTTP_AUTHORIZATION' in context.request.environ:
                    return

                # Check that the basic scheme was requested
                scheme, credentials = context.request.get('HTTP_AUTHORIZATION').split(' ', 1)
                if scheme.lower() != 'basic':
                    raise HTTPBadRequest('Authentication scheme not supported')

                # Base64 decode the contents of the Authorization header
                username, password = b64decode(credentials).split(':', 1)

                # Attempt to authenticate the user, send a 401 response if it fails
                if not username or not self.authenticate(context, username, password, 'request'):
                    context.response.headers['WWW-Authenticate'] = 'Basic realm="%s"' % options['realm']
                    raise HTTPUnauthorized
            elif options['method'] == 'session':
                uid = context.session.get(options['sessionkey'])
                if uid is not None:
                    context.user = options['lookup_callback'](context, uid)

    def after(self, context, exc=None):
        # An HTTPForbidden exception when authentication has not happened means that the application wants
        # HTTP authentication, so a challenge should be sent to the client
        if isinstance(exc, HTTPForbidden) and context._authentication_options['method'] == 'basic' and not context.user:
            context.response.headers['WWW-authenticate'] = 'Basic realm="%s"' % context._authentication_options['realm']
            raise HTTPUnauthorized

    @staticmethod
    def authenticate(context, username, password=None, save_session=None):
        """Authenticate a user.

        Sets the current user in the context and template namespace if successful.
        You can optionally omit the password and force the authentication to authenticate as any user.
        If @save_session@ is @True@, save the authentication information in the session.
        If @save_session@ is omitted, authentication information is saved in the session if the authentication
        method has been set to @session@.

        If successful, the context.user variable is immediately available.

        Returns @True@ on success, @False@ otherwise.
        """

        options = context._authentication_options
        result = options['auth_callback'](context, username, password)
        if result is None or result[1] is None:
            return False

        # Save the user ID to the session if configured or explicitly requested to do so
        if save_session or (save_session is None and options['method'] == 'session'):
            if not hasattr(context, 'session'):
                raise Exception('Cannot save authentication information to session -- the session extension has not been configured')  # TODO: refine exception
            context.session[options['sessionkey']] = result[0]
            context.session.save()

        # Add the "user" variable to the template namespace
        context.user = result[1]
        if hasattr(context, 'namespace'):
            context.namespace.user = result[1]

        return True

    @staticmethod
    def deauthenticate(context, nuke=False):
        """Force logout.

        The context.user variable and the session variable are immediately cleared.

        Additionally, this function can also completely erase the session.
        """

        options = context._authentication_options
        session = getattr(context, 'session', None)
        if session:
            if nuke:
                session.invalidate()

            session.pop(options['sessionkey'], None)

            if not session.autocommit:
                session.save()

        context.user = None
