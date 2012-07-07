# encoding: utf-8

"""Dialect API / interface."""


__all__ = ['Dialect']


class Dialect(object):
    """A basic method of dispatching requests from WSGI.

    Subclasses allow for extreme levels of control over how content is found
    and returned to the end user.

    Examples include the basic object-dispatch Controller, the Routes-based
    RoutingController for improved performance, XMLRPCController, or
    AMFController for Flash/Flex integration.

    These are called dialects due to the fact that XML-RPC and AMF, and
    potentially future protocols, are fundamentally different to standard
    HTTP file-based operation, despite operating over HTTP.
    """

    def __call__(self, request):
        """Controller base classes implement this.

        This takes no arguments (all input should be processed from the request object)
        and should return content to the higher level processing middleware.
        """
        raise NotImplementedError
