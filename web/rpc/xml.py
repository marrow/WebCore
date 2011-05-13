"""A basic XML-RPC Dialect class."""

import xmlrpclib

from webob.exc import *

from web.core import Dialect, response
from web.rpc import route

log = __import__('logging').getLogger(__name__)


class XMLRPCController(Dialect):
    __allow_none__ = False
    __max_body_length__ = 4194304

    def _fault(self, code, message, *args):
        """Return a formatted XMLRPC Fault response."""

        fault = xmlrpclib.Fault(code, message % args)
        return xmlrpclib.dumps(fault, methodresponse=True)

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

        args, method = xmlrpclib.loads(request.body, True)

        log.debug("XML-RPC Call: %s%r", method, args)

        func, parent = route(self, method, XMLRPCController)

        log.debug("Found method: %r", func)

        try:
            args = parent.__before__(*args)

        except AttributeError:
            pass

        result = func(*args)

        try:
            result = parent.__after__(result, *args)

        except AttributeError:
            pass

        log.debug("Got result: %r", result)

        response.content_type = 'text/xml'
        return xmlrpclib.dumps((result,), methodresponse=True,
                               allow_none=self.__allow_none__)
