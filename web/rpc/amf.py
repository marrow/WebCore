# encoding: utf-8

"""A basic AMF Dialect class."""

import web

from functools import wraps
from web.rpc import route

try:
    import pyamf.remoting.gateway
except ImportError:  # pragma: no cover
    raise ImportError("If you want to use the AMFController class, you must install PyAMF.")


__all__ = ['AMFController']
log = __import__('logging').getLogger(__name__)


class AMFController(web.core.Dialect):
    __gateway__ = dict()

    def __init__(self):
        self._gateway = pyamf.remoting.gateway.BaseGateway(logger=log, *self.__gateway__)

    def _call(self, fn, parent):
        @wraps(fn)
        def inner(*args, **kw):
            callback = getattr(parent, '__before__', None)
            if callback:
                args = parent.__before__(*args)

            result = fn(*args, **kw)

            callback = getattr(parent, '__after__', None)
            if callback:
                result = parent.__after__(result, *args)

            return result

        return inner

    def __call__(self, request):
        pyamf_request = pyamf.remoting.decode(request.body)
        pyamf_response = pyamf.remoting.Envelope(pyamf_request.amfVersion)

        for name, message in pyamf_request:
            # Dynamically build mapping.
            # This introduces a performance hit on the first request of each method.
            if message.target not in self._gateway.services:
                fn, parent = route(self, message.target, AMFController)
                self._gateway.addService(self._call(fn, parent), message.target)

            pyamf_response[name] = self._gateway.getProcessor(message)(message)

        web.core.response.headers['Content-Type'] = pyamf.remoting.CONTENT_TYPE

        return pyamf.remoting.encode(pyamf_response).getvalue()
