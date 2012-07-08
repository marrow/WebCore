# encoding: utf-8

"""A Dialect class that implements the JSON-RPC protocol (version 1.0)."""

import web.core

from web.core import Dialect
from web.core.http import HTTPBadRequest, HTTPMethodNotAllowed
from web.rpc import route
from marrow.util.compat import exception

try:
    from simplejson import loads
except ImportError:
    from json import loads


log = __import__('logging').getLogger(__name__)


class JSONRPCController(Dialect):
    def __call__(self, request):
        """Parse the JSON body and dispatch."""

        if request.method != 'POST':
            raise HTTPMethodNotAllowed("POST required.")

        try:
            json = loads(request.body)
        except ValueError:
            raise HTTPBadRequest("Unable to parse JSON request.")

        for key in ('method', 'id'):
            if key not in json:
                raise HTTPBadRequest("Missing required JSON-RPC value: " + key)

        method = json['method']
        args = json.get('params', [])
        id_ = json['id']

        if not isinstance(args, list):
            raise HTTPBadRequest("Bad parameters, must be a list: {0!r}".format(args))

        log.debug("JSON-RPC Call: %s%r", method, args)

        func, parent = route(self, method, JSONRPCController)

        log.debug("Found method: %r", func)

        try:
            callback = getattr(parent, '__before__', None)
            if callback:
                args = callback(*args)

            result = func(*args)
            error = None

            callback = getattr(parent, '__after__', None)
            if callback:
                result = callback(result, *args)
        except:
            log.exception("Error calling RPC mechanism.")
            exc = exception()

            web.core.response.status_int = 500

            result = None
            error = dict(
                    name='JSONRPCError',
                    code=100,
                    message=str(exc.exception),
                    error="Not disclosed." if not web.core.config.get('debug', False) else exc.formatted
                )
        else:
            log.debug("Got result: %r", result)

        if id_ is not None:
            web.core.response.content_type = 'application/json'
            return 'json:', dict(result=result, error=error, id=id_)
