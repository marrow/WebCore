# coding: utf-8
from __future__ import unicode_literals, division, print_function, absolute_import

import functools

from marrow.wsgi.exceptions import HTTPForbidden, HTTPUnauthorized

__all__ = ['authorize', 'all', 'any', 'not_', 'authenticated', 'unauthenticated']


def _default_action(context):
    # If the user is unauthenticated and HTTP authentication was requested, return a 401 with the challenge instead
    # of a 403 error
    if getattr(context, 'user', None) is None:
        challenge = context._authentication_options.get('challenge')
        if challenge:
            exc = HTTPUnauthorized()
            exc.headers.append((b'WWW-Authenticate', challenge))
            raise exc

    raise HTTPForbidden


def authorize(predicate, action=_default_action):
    """Decorator to enforce predicates.

    Calls the given predicate with the current context.
    If the return value evaluates to @False@, execute the given action with @context@ as the single argument,
    or raise HTTPForbidden (HTTP code 403) if no action is specified.
    """

    if not callable(action):
        raise TypeError('action must be callable, got {0} instead'.format(type(action)))

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            self = func.__call__.__self__
            context = self._ctx if self is not func else args[0]
            if predicate(context):
                return func(*args, **kw)

            action(context)

        return wrapper

    return decorator


def all(*predicates):
    """Returns @True@ if all of the given predicates return @True@."""

    def wrapper(context):
        for predicate in predicates:
            if not predicate(context):
                return False
        return True
    return wrapper


def any(*predicates):
    """Returns @True@ if any of the given predicates return @True@."""

    def wrapper(context):
        for predicate in predicates:
            if predicate(context):
                return True
        return False
    return wrapper


def not_(predicate):
    """Negates the return value of the wrapped predicate."""

    def wrapper(context):
        return not predicate(context)
    return wrapper


def authenticated(context):
    """Returns @True@ if the user has been authenticated for this request."""

    return getattr(context, 'user', None) is not None


def unauthenticated(context):
    """Returns @True@ if the user has not been authenticated for this request."""

    return getattr(context, 'user', None) is None
