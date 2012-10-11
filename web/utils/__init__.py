# encoding: utf-8

"""WebCore-specific utilities."""

from marrow.util.url import URL


__all__ = ['URLGenerator']


class URLGenerator(object):
    @property
    def _base(self):
        """Return a 3-tuple of the application base path, current processed
        script_path, and the script_path"""
        import web.core
        r = web.core.request
        return r.environ['web.base'], r.path_url, r.environ['web.controller']
    
    def __call__(self, path=None, params=None, anchor=None, protocol=None, host=None, port=None):
        """The default syntax for the creation of paths.
        
        Path must be a string. Params must be a dictionary and represents the
        query string arguments. Anchor must be a string representing the text
        after the hash symbol. Host must be a string. Port must be an integer.
        
        If protocol, host, or port are defined then a full URL will be
        generated, otherwise an absolute path will be generated.
        
        If the path begins with a forward slash it is absolute from the root
        of the web application mount point, otherwise it is relative to the
        current controller (not method).
        
        Query string arguments may be strings, or lists of strings. A list
        indicates an argument that appears multiple times.
        
        For example, url('/foo') will result in a url of '/app/foo' if the
        application is mounted on /app.  If you are within a controller named
        'users' attached to your appliation root, you can use url('create') to
        generate the URL needed to call the 'create' method;
        "/app/users/create" in this case.
        
        To switch to a secure connection without changing the URL you can call
        url(protocol='https').
        """
        if protocol or host or port:
            return self._full(path, params, anchor, protocol, host, port)
        
        return self._partial(path, params, anchor)
    
    def complete(self, path=None, params=None, anchor=None, protocol=None, host=None, port=None):
        """As per the default syntax, but always returns a complete URL."""
        
        return self._full(path, params, anchor, protocol, host, port)
    
    def compose(self, *args, **kw):
        """An alternate syntax for simpler URL generation.
        
        This accepts an unlimited number of positional arguments which will be
        composed into the path and keyword arguments will be used as query
        string arguments.  If the first path element starts with a forward
        slash then the path is absolute from the root of the application mount
        point, otherwise it is relative to the current controller (not method).
        
        Query string arguments may be strings, or lists of strings. A list
        indicates an argument that appears multiple times.
        
        This syntax does not allow overriding of other URL elements (such as
        protocol and host) and thus never generates full URLs, nor does it
        allow the definition of an anchor.
        
        This is most useful if you are using a CRUD controller style. For
        example, if the user is viewing a listing generated on /app/users/
        you can use the following to good effect:
        
        * url.compose('create') - "/app/users/create"
        * url.compose(user.id) - "/app/users/27"
        * url.compose(user.id, 'modify') - "/app/users/27/modify"
        """
        
        return self('/'.join(str(i) for i in args), kw)
    
    def _full(self, path, params, anchor, protocol, host, port):
        """Prepare a complete URL."""
        
        base, current, controller = self._base
        url = URL(current)
        
        url.path = self._partial(path, None, None)
        
        if protocol:
            url.scheme = protocol
        
        if host:
            url.host = host
        
        if port:
            url.port = port
        
        url.query = params
        url.fragment = anchor
        
        return unicode(url)
    
    def _partial(self, path, params, anchor):
        """Prepare a resource path."""
        
        base, current, controller = self._base
        url = URL()
        
        if not path:
            url.path = str(URL(current).path)
        else:
            url.path = base if path.startswith('/') else controller
            url.path.append(path[1:] if path.startswith('/') else path)
        
        url.query = params
        url.fragment = anchor
        
        return unicode(url)
