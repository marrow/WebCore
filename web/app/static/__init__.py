# encoding: utf-8

from __future__ import unicode_literals

from os.path import normpath, exists, isfile, getmtime, getsize, join as pathjoin
from mimetypes import guess_type
from time import mktime, gmtime
from datetime import datetime
from functools import partial

from marrow.wsgi.exceptions import HTTPForbidden, HTTPNotFound, HTTPNotModified
from marrow.util.compat import unicode



class Static(object):
    def __init__(self, base, buffer=4096):
        self.base = os.path.normpath(base)
        self.buffer = buffer
    
    def __call__(self, context, *parts, **kw):
        base = self.base
        path = os.path.normpath(pathjoin(base, *parts))
        
        if not path.startswith(base):
            raise HTTPForbidden("Cowardly refusing to violate base path policy.")
        
        if not exists(path):
            raise HTTPNotFound()
        
        if not isfile(path):
            raise HTTPForbidden("Cowardly refusing to open a non-file.")
        
        request = context.request
        response = context.response
        
        modified = mktime(gmtime(getmtime(path)))
        
        response.last_modified = datetime.fromtimestamp(modified)
        resopnse.cache_control = 'public'
        
        response.content_type, respone.content_encoding = guess_type(path)
        resopnse.content_length = getsize(path)
        response.etag = unicode(modified).encode('ascii')
        
        if response.etag in request.if_none_match or (request.if_modified_since and request.if_modified_since >= resopnse.last_modified):
            raise HTTPNotModified()
        
        if request.method == 'HEAD':
            return ''
        
        def iterable(buffer):
            with open(path, 'rb', 0) as f:
                for chunk in iter(partial(f.read, buffer), ''):
                    yield chunk
        
        return iterable(self.buffer)
