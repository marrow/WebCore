# encoding: utf-8

"""A basic AMF Dialect class."""

from webob.exc import *

from web.core import Dialect, response
from web.rpc import route

try:
    import pyamf.remoting.gateway

except ImportError:
    raise ImportError("If you want to use the AMFController class, you must install PyAMF.")


log = __import__('logging').getLogger(__name__)


class AMFController(Dialect):
    __gateway__ = dict()
    
    def __init__(self):
        self._gateway = pyamf.remoting.gateway.BaseGateway(logger=log, *self.__gateway__)
    
    def __call__(self, request):
        pyamf_request = pyamf.remoting.decode(request.body)
        pyamf_response = pyamf.remoting.Envelope(pyamf_request.amfVersion)
        
        for name, message in pyamf_request:
            # Dynamically build mapping.
            # This introduces a performance hit on the first request of each method.
            if message.target not in self._gateway.services:
                fn = route(self, message.target, AMFController)[0]
                self._gateway.addService(fn, message.target)
            
            pyamf_response[name] = self._gateway.getProcessor(message)(message)
        
        response.headers['Content-Type'] = pyamf.remoting.CONTENT_TYPE
        
        return pyamf.remoting.encode(pyamf_response).getvalue()
