# encoding: utf-8

import re
import time
import datetime

import webob

import web
from web.core.middleware import middleware, defaultbool
from web.utils.object import get_dotted_object
from paste.deploy.converters import asbool, asint, aslist

from pymongo.binary import Binary
from pymongo.objectid import ObjectId
from pymongo.dbref import DBRef
from pymongo.code import Code


__all__ = ['ConstantProfile', 'cprofile']
log = __import__('logging').getLogger(__name__)


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


class ConstantProfile(object):
    def __init__(self, application, config=dict()):
        if 'web.profile.db' not in config:
            raise Exception('You must define a "web.profile.db" database object.')
        
        self.application = application
        
        db = get_dotted_object(config['web.profile.db'])
        self.collection = db[config.get('web.profile.collection', 'profiler')]
        
        self.exclude = [i.strip() for i in config.get('web.profile.exclude', '/static, /stats').split(',')]
    
    def __call__(self, environ, start_response):
        resp = []
        
        def local_start(*args, **kw):
            resp.extend(args)
            start_response(*args, **kw)
        
        environ['cprofile.start'] = time.time()
        result = self.application(environ, local_start)
        environ['cprofile.end'] = time.time()
        
        try:
            start = time.time()
            record = dict()
            request = webob.Request(environ)
        
            if 'Cookie' in request.headers:
                del request.headers['Cookie']
        
            record['path'] = request.script_name + (request.path_info if request.path_info else '')
        
            for i in self.exclude:
                """Allow specific paths to be excluded from the profiling."""
                if record['path'].startswith(i):
                    log.debug("Not logging profile information.")
                    return result
        
            log.debug('Logging %r because it doesn\'t fit in %r', record['path'], self.exclude)
        
            record['version'] = 1
            record['status'] = dict(code=int(resp[0].split(' ', 1)[0]), string=resp[0])
            record['environ'] = dict([(i, j) for i, j in environ.iteritems() if (not i.startswith('HTTP_') and i == i.upper())])
            record['request'] = dict([(i.lower(), j) for i, j in request.headers.iteritems()])
            record['response'] = dict([(i.lower(), j) for i, j in resp[1]])
            record['wsgi'] = dict([(i.replace('.', '-'), repr(j)) for i, j in environ.iteritems() if ('.' in i)])
            record['session'] = dict(
                    id = environ['beaker.session'].id if 'beaker.session' in environ else None,
                    contents = dict(environ['beaker.session']) if 'beaker.session' in environ else None
                )
            record['profile'] = dict(
                    range = dict(
                            start = environ['cprofile.start'],
                            end = environ['cprofile.end']
                        ),
                    duration = (environ['cprofile.end'] - environ['cprofile.start']) * 1000
                )
        
            self.collection.insert(desc_dict(record))
            self.collection.insert(dict(version=0, duration=(time.time() - start) * 1000))
        
        except:
            log.exception("Error processing performance information.")

        return result


@middleware('profiling', after="compression")
def cprofile(app, config):
    if not config.get('web.profile', '') == 'constant':
        return app

    log.debug("Enabling constant profiling support.")

    return ConstantProfile(app, config)
