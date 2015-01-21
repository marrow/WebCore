# encoding: utf-8

"""A Dialect class that implements Sencha's Ext Direct protocol."""
import inspect
import sys
from types import MethodType

import web.core
from web.core import Dialect
from web.core.http import HTTPBadRequest, HTTPMethodNotAllowed

try:
    from simplejson import loads, dumps
except ImportError:
    from json import loads, dumps


log = __import__('logging').getLogger(__name__)


class ExtDirectController(Dialect):
    _api = None
    _action_map = None
    
    def _configure_api(self):
        methods = []
        self._api = {self.__class__.__name__: methods}
        self._action_map = {self.__class__.__name__: self}
        
        for attr in dir(self):
            if attr.startswith('_'):
                continue
            
            value = getattr(self, attr)
            if isinstance(value, MethodType):
                spec = inspect.getargspec(value)
                methods.append({
                    'name': attr,
                    'len': len(spec.args) - 1
                })
            elif isinstance(value, ExtDirectController):
                value._configure_api()
                self._api.update(value._api)
                self._action_map.update(value._action_map)
    
    def _get_api(self):
        if self._api is None:
            self._configure_api()
        
        return 'json:', self._api
    
    def __call__(self, request):
        if request.method == 'GET':
            return self._get_api()
        if request.method != 'POST':
            raise HTTPMethodNotAllowed("GET or POST required.")
        
        if request.POST:
            rpc_request = request.POST.mixed()
        else:
            try:
                rpc_request = loads(request.body)
            except ValueError:
                raise HTTPBadRequest("Unable to parse JSON request.")
        
        if self._api is None:
            self._configure_api()
        
        responses = []
        if isinstance(rpc_request, list):
            requests = rpc_request
        else:
            requests = [rpc_request]
            is_upload = 'extUpload' in rpc_request
        
        for json in requests:
            if 'extAction' in json:
                # Form post
                for key in ('extAction', 'extMethod', 'extTID'):
                    if key not in json:
                        raise HTTPBadRequest("Missing required key in request: " + key)
                
                type_ = json.pop('extType')
                action = json.pop('extAction')
                method = json.pop('extMethod')
                tid = json.pop('extTID')
                is_upload = json.pop('extUpload', None) == 'true'
                args = ()
                kwargs = json
            else:
                # XMLHTTPRequest
                for key in ('type', 'action', 'method', 'tid'):
                    if key not in json:
                        from nose.tools import set_trace; set_trace()
                        raise HTTPBadRequest("Missing required key in request: " + key)
                
                type_ = json['type']                
                action = json['action']
                method = json['method']
                tid = json['tid']
                args = json.get('data', [])
                kwargs = {}
                is_upload = False
            
            if type_ != 'rpc':
                raise HTTPBadRequest("Only RPC requests are supported")
            if not isinstance(args, (list, tuple)):
                raise HTTPBadRequest("Bad parameters, must be an array: {0!r}".format(args))
            
            log.debug("Ext Direct Call: %s.%s%r", action, method, args)
            
            try:
                parent = self._action_map[action]
            except KeyError:
                raise HTTPBadRequest("Target class not found: %s", action)
            
            try:
                func = getattr(parent, method)
            except AttributeError:
                raise HTTPBadRequest("Target method not found: %s.%s", action, method)
            
            log.debug("Found method: %r", func)
            
            response = {
                'type': 'rpc',
                'tid': tid,
                'action': action,
                'method': method
            }
            responses.append(response)
            
            try:
                callback = getattr(parent, '__before__', None)
                if callback:
                    args = callback(*args, **kwargs)
                
                result = func(*args, **kwargs)
                
                callback = getattr(parent, '__after__', None)
                if callback:
                    result = callback(result, *args, **kwargs)
                
                log.debug("Got result: %r", result)
                response['result'] = result
            except:
                log.exception("Error in Ext Direct call.")
                web.core.response.status_int = 500
                
                # Get the last traceback object which shows where the exception was actually raised
                exc, tb = sys.exc_info()[1:]
                while tb.tb_next:
                    tb = tb.tb_next
                
                response.update({
                    'type': 'exception',
                    'message': str(exc),
                    'where': '{0}:{1}'.format(tb.tb_frame.f_code.co_filename, tb.tb_frame.f_lineno)
                })
        
        if is_upload:
            encoded_response = dumps(responses[0]).replace('"', r'\"')
            return '<html><body><textarea>%s</textarea></body></html>' % encoded_response
        else:
            web.core.response.content_type = 'application/json'
            return 'json:', responses[0] if len(responses) == 1 else responses
