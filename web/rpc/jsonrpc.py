# encoding: utf-8

"""A JSON-RPC Dialect class."""

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
        """Parse an XML-RPC body and dispatch."""
        
        if request.method != 'POST':
            raise HTTPMethodNotAllowed("POST required.")
        
        try:
            json = loads(request.body)
        except ValueError:
            raise HTTPBadRequest("Unable to parse JSON request.")
        
        for key in ('method', 'params'):
            if key not in json:
                raise HTTPBadRequest("Missing required JSON-RPC value: " + key)
        
        method = json['method']
        args = json['params']
        id = json.get('id', None)
        
        if not isinstance(args, list):
            raise HTTPBadRequest("Bad paramaters, must be a list: {0!r}".format(args))
        
        log.debug("JSON-RPC Call: %s%r", method, args)
        
        func, parent = route(self, method, JSONRPCController)
        
        log.debug("Found method: %r", func)
        
        try:
            args = parent.__before__(*args)
        except AttributeError:
            pass
        
        try:
            result = func(*args)
        except:
            exc = exception()
            
            web.core.response.status_int = 500
            web.core.response.content_type = 'application/json'
            
            return 'json:', dict(result=None, error=dict(
                    name = 'JSONRPCError',
                    code = 100,
                    message = str(exc.exception),
                    error = "Not disclosed." if not web.core.config.get('debug', False) else exc.formatted
                ), id=id)
        
        try:
            result = parent.__after__(result, *args)
        except AttributeError:
            pass
        
        log.debug("Got result: %r", result)
        
        web.core.response.content_type = 'application/json'
        
        if id:
            return 'json:', dict(result=result, error=None, id=id)
        
        return ''
