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
        default_options.setdefault('action', None)
        default_options.setdefault('realm', None)
        default_options.setdefault('sessionkey', '__user_id')

        self._validate_options(default_options)
        if self.default_options['method'] == 'session':
            self.needs = ['session']

    @staticmethod
    def _validate_options(options):
        if options['method'] not in ('basic', 'session'):
            raise ValueError('Invalid value for option "method": %s' % options['method'])

        if not 'callback' in options:
            raise ValueError('Missing required option: callback')
        callback = options['callback']
        if not callable(callback):
            raise ValueError('Option "callback" must be a callable, got %r instead' % type(callback))

        action = options.get('action')
        if isinstance(action, unicode):
            action = action.encode('iso-8859-1')
        elif action is not None and not isinstance(action, bytes) and not callable(action):
            raise ValueError('Option "action" must be None, a string or a callable -- got %r instead' % type(action))

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
        if 'namespace' in context:
            context.namespace.user = None

    def prepare(self, context):
        context.authenticate = partial(self.authenticate, context)
        context.deauthenticate = partial(self.deauthenticate, context)

    def dispatch(self, context, consumed, handler, is_endpoint):
        if is_endpoint:
            # Determine the credentials to authenticate with, based on the configured method
            options = context._authentication_options
            method = context.get('_authentication_method', self.default_method)
            if method == 'basic':
                if not 'authorization' in context.request:
                    context.response.headers['WWW-authenticate'] = 'Basic realm="%s"' % options['realm']
                    raise HTTPUnauthorized

                scheme, credentials = context.request.get('HTTP_AUTHORIZATION').split(' ', 1)
                if scheme.lower() != 'basic':
                    raise HTTPBadRequest('Authentication scheme not supported')

                username, password = b64decode(credentials).split(':', 1)
                session, scope = False, 'request'
            elif method == 'session':
                username = context.session.get(options['sessionkey'])
                password = None
                session, scope = True, 'session'

            # Attempt to authenticate the user, and execute the configured action if that fails
            if not username or not self.authenticate(context, username, password, session, scope):
                action = options['action']
                if action is None:
                    raise HTTPForbidden
                if isinstance(action, bytes):
                    raise HTTPTemporaryRedirect(location=action)
                action(context)
        elif hasattr(handler, '__auth__'):
            context._authentication_options.update(handler.__auth__)
            self._validate_options(context._authentication_options)

    def authenticate(self, context, username, password=None, scope='session'):
        """Authenticate a user.

        Sets the current user in the session. You can optionally omit the password
        and force the authentication to authenticate as any user.

        If successful, the context.user variable is immediately available.

        Returns @True@ on success, @False@ otherwise.
        """

        options = context._authentication_options
        result = options['callback'](context, username, password)
        if result is None or result[1] is None:
            return False

        if scope == 'session':
            context.session[self.sessionkey] = result[0]
            context.session.save()

        context.user = result[1]
        if 'namespace' in context:
            context.namespace.user = result[1]

        return True

    def deauthenticate(self, context, nuke=False):
        """Force logout.

        The context.user variable and the session variable are immediately cleared.

        Additionally, this function can also completely erase the session.
        """

        options = context._authentication_options
        session = getattr(context, 'session')
        if session:
            if nuke:
                session.invalidate()

            session.pop(options['sessionkey'], None)

            if not session.autocommit:
                session.save()

        context.user = None
