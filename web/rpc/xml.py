# encoding: utf-8

"""A basic XML-RPC Dialect class."""

import xmlrpclib

import web

from marrow.util.bunch import Bunch
from marrow.util.object import getargspec
from webob.exc import HTTPException

from web.core.http import HTTPLengthRequired, HTTPRequestEntityTooLarge
from web.rpc import route, RoutingError


__all__ = ['XMLRPCController']
log = __import__('logging').getLogger(__name__)


fault = Bunch(
        parse=Bunch(
                badly_formed=(-32700, "Not well formed."),
                bad_encoding=(-32701, "Unsupported encoding."),
                bad_characte=(-32702, "Character not supported by encoding.")
            ),
        server=Bunch(
                invalid=(-32600, "XML-RPC request does not conform to specification."),
                notfound=(-32601, "Requested method not found."),
                params=(-32602, "Invalid parameters to method."),
                internal=(-32603, "Internal error.")
            ),
        other=Bunch(
                application=(-32500, "Application error."),
                system=(-32400, "System error."),
                transport=(-32300, "Transport error.")
            )
    )


class XMLRPCController(web.core.Dialect):
    __allow_none__ = False
    __max_body_length__ = 4194304

    def _fault(self, fault):
        """Return a formatted XML-RPC Fault response."""

        log.debug("Encountered fault: %d %s", *fault)

        fault = xmlrpclib.Fault(fault[0], fault[1])
        web.core.response.content_type = 'text/xml'
        return xmlrpclib.dumps(fault, methodresponse=True)

    def _response(self, value):
        """Return a formatted XML-RPC response."""

        log.debug("Got result: %r", value[0])

        try:
            value = xmlrpclib.dumps(value, methodresponse=True, allow_none=self.__allow_none__)
        except:
            return self._fault(fault.other.application)

        web.core.response.content_type = 'text/xml'
        return value

    def __call__(self, request):
        """Parse an XML-RPC body and dispatch."""

        length = int(request.headers.get('Content-Length', 0))

        if not length:
            log.debug("No content length specified, returning 411 HTTPLengthRequired error.")
            raise HTTPLengthRequired()

        if not length or length > self.__max_body_length__:
            log.debug("Content length larger than allowed maximum of %d bytes, "
                      "returning 413 HTTPRequestEntityTooLarge error.",
                      self.__max_body_length__)
            raise HTTPRequestEntityTooLarge("XML body too large.")

        try:
            args, method = xmlrpclib.loads(request.body, True)
        except:
            return self._fault(fault.parse.badly_formed)

        log.debug("XML-RPC Call: %s%r", method, args)

        try:
            func, parent = route(self, method, XMLRPCController)
        except RoutingError:
            return self._fault(fault.server.notfound)

        log.debug("Found method: %r", func)

        cargs, cdefaults, unlimited = getargspec(func)[:3]
        cargs = len(cargs)
        cdefaults = len(cdefaults)
        nargs = len(args)

        if nargs < cargs - cdefaults or (not unlimited and nargs > cargs):
            return self._fault(fault.server.params)

        try:
            callback = getattr(parent, '__before__', None)
            if callback:
                args = parent.__before__(*args)

            result = func(*args)

            callback = getattr(parent, '__after__', None)
            if callback:
                result = parent.__after__(result, *args)
        except HTTPException:
            raise
        except:
            log.error("Error calling RPC mechanism.", exc_info=True)
            return self._fault(fault.other.application)

        return self._response((result,))
