# encoding: utf-8

import re
import time
import datetime

import web
from web.core.middleware import middleware, defaultbool


__all__ = ['ConstantProfile', 'cprofile']
log = __import__('logging').getLogger(__name__)



class ConstantProfile(object):
    def __init__(self, application, config=dict()):
        from pymongo.connection import Connection
        
        self.application = application
        self.connection = Connection("localhost")
        self.db = self.connection.profiler
        self.db.authenticate("yapwf", "yapwf")
        self.requests = self.db.requests
        
        self.base = dict(
                hostname = 'HTTP_HOST',
                remote = 'REMOTE_ADDR',
                method = 'REQUEST_METHOD',
                script = 'SCRIPT_NAME',
                duration = 'cprofile.duration'
            )
    
    
    
    def __call__(self, environ, start_response):
        from pymongo.binary import Binary
        from pymongo.objectid import ObjectId
        from pymongo.dbref import DBRef
        from pymongo.code import Code
        
        environ['cprofile.start'] = time.time()
        
        result = self.application(environ, start_response)
        
        clean_environ = dict()
        
        def desc_dict(d):
            cd = dict()
            
            for i, j in d.iteritems():
                n = i.replace('.', '_')
                
                if isinstance(j, dict):
                    cd[n] = desc_dict(j)
                    continue
                
                if isinstance(j, (list, tuple, set)):
                    cd[n] = []
                    
                    for k in j:
                        if isinstance(k, (basestring, int, long, float, bool, datetime.datetime)) or k is None:
                            cd[n].append(k)
                        else:
                            cd[n].append(repr(k))
                    
                    continue
                
                if not isinstance(j, (basestring, int, long, float, bool, datetime.datetime)) and j is not None:
                    cd[n] = repr(j)
                    continue
                
                cd[n] = j
            
            return cd
        
        environ.update({
                'cprofile.duration': time.time() - environ['cprofile.start'],
                'beaker.session_id': environ['beaker.session'].id if 'beaker.session' in environ else None
            })
        
        self.requests.insert(desc_dict(environ))

        return result


@middleware('profiling', after="compression")
def cprofile(app, config):
    if not config.get('web.profile', '') == 'constant':
        return app

    log.debug("Enabling constant profiling support.")

    return ConstantProfile(app, config)