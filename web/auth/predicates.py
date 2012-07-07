# encoding: utf-8

import web


__all__ = [
        'Predicate', 'CustomPredicate',
        'Not', 'All', 'Any', 'always', 'never',
        'anonymous', 'authenticated',
        'AttrIn', 'ValueIn', 'EnvironIn'
    ]


class Predicate(object):
    def __nonzero__(self):
        raise NotImplementedError('Subclasses override this method.')


class CustomPredicate(Predicate):
    """Build your own advanced predicates by passing in a callable (usually a lambda anonymous function).

    E.g. # useful for a MongoDB back-end
         UserHasFooAttr = CustomPredicate(lambda u, r: hasattr(u, 'foo'))
    """

    def __init__(self, conditional):
        super(CustomPredicate, self).__init__()
        self.conditional = conditional

    def __nonzero__(self):
        return bool(self.conditional(web.auth.user, web.core.request))


class Not(Predicate):
    """True if the argument is False.

    For immediate evaluation, the 'not' operation is more efficient.
    """

    def __init__(self, arg):
        super(Not, self).__init__()
        self.arg = arg

    def __nonzero__(self):
        return not bool(self.arg)


class All(Predicate):
    """True if all of the arguments are True.

    Equivalent to an 'and' operation between all arguments.

    For immediate evaluation, use the 'and' operation or the 'all' built-in.
    """

    def __init__(self, *args):
        super(All, self).__init__()
        self.args = args

    def __nonzero__(self):
        return all(self.args)


class Any(Predicate):
    """True if any of the arguments are True.

    Equivalent to an 'or' operation between all arguments.

    For immediate evaluation, use the 'or' operation or the 'any' built-in.
    """

    def __init__(self, *args):
        super(Any, self).__init__()
        self.args = args

    def __nonzero__(self):
        return any(self.args)


class Always(Predicate):
    """Always True.

    Included for completeness sake.
    """

    def __nonzero__(self):
        return True

always = Always()


class Never(Predicate):
    """Always False.

    Included for completeness sake.
    """

    def __nonzero__(self):
        return False

never = Never()


class Anonymous(Predicate):
    """True if no user is currently logged in."""

    def __nonzero__(self):
        return web.auth.user is None or web.auth.user._current_obj() is None

anonymous = Anonymous()


class Authenticated(Predicate):
    """True if a user is currently logged in."""

    def __nonzero__(self):
        return web.auth.user is not None and web.auth.user._current_obj() is not None

authenticated = Authenticated()


class AttrIn(Predicate):
    """True if the an attribute matches an element in an iterable.

    E.g. higher_ups = AttrIn('username', ['admin', 'jrh'])

    E.g. UserNameIn = AttrIn.partial('username')
         higher_ups = UserNameIn(['admin', 'jrh'])
    """

    def __init__(self, attr, values=[]):
        super(AttrIn, self).__init__()
        self.attr = attr
        self.values = values if isinstance(values, list) else [values]

    def __nonzero__(self):
        return getattr(web.auth.user, self.attr, None) in self.values

    @classmethod
    def partial(cls, attr):
        """Use this method to prepare your own advanced predicate templates."""
        class PartialAttrIn(cls):
            def __init__(self, values=[]):
                super(PartialAttrIn, self).__init__(attr, values)

        return PartialAttrIn


class ValueIn(Predicate):
    """True if a value matches an attribute, where the attribute is an iterable.

    E.g. administrators = ValueIn('admin', 'group_names')
    E.g. editors = ValueIn('editor', 'roles')

    E.g. HasGroup = ValueIn.partial('group_names')
    E.g. HasRole = ValueIn.partial('roles')
    """

    def __init__(self, value, attr):
        super(ValueIn, self).__init__()
        self.value = value
        self.attr = attr

    def __nonzero__(self):
        return self.value in getattr(web.auth.user, self.attr, [])

    @classmethod
    def partial(cls, attr):
        """Use this method to prepare your own advanced predicate templates."""
        class PartialValueIn(cls):
            def __init__(self, value):
                super(PartialValueIn, self).__init__(value, attr)

        return PartialValueIn


class EnvironIn(Predicate):
    """True if a environment variable matches an element in an iterable.

    E.g. local = EnvironIn('REMOTE_ADDR', ['127.0.0.1', '::1', 'fe80::1%%lo0'])

    E.g. RemoteAddressIn = EnvironIn.partial('REMOTE_ADDR')
         local = RemoteAddressIn(['127.0.0.1', '::1', 'fe80::1%%lo0'])
    """

    def __init__(self, key, values=[]):
        super(EnvironIn, self).__init__()
        self.key = key
        self.values = values if isinstance(values, list) else [values]

    def __nonzero__(self):
        return web.core.request.environ.get(self.key, None) in self.values

    @classmethod
    def partial(cls, attr):
        """Use this method to prepare your own advanced predicate templates."""
        class PartialEnvironIn(cls):
            def __init__(self, values=[]):
                super(PartialEnvironIn, self).__init__(attr, values)

        return PartialEnvironIn
