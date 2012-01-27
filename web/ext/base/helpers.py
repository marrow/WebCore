# encoding: utf-8

import weakref
import math

from marrow.util.url import URL


__all__ = ['URLGenerator', 'Pager']


class URLGenerator(object):
    __slots__ = ('_ctx', )
    
    def __init__(self, context):
        self._ctx = weakref.proxy(context)
    
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
        ctx = self.ctx
        base = ctx.environ['web.base']
        current = ctx.request.path
        controller = ctx.path[-1]
        
        url = URL(current)
        
        url.path = self._partial(path, None, None)
        
        if protocol:
            url.scheme = protocol
        
        if host:
            url.host = host
        
        if port:
            url.port = port
        
        url.params = params
        url.fragment = anchor
        
        return str(url)
    
    def _partial(self, path, params, anchor):
        ctx = self.ctx
        base = ctx.environ['web.base']
        current = ctx.request.path
        controller = ctx.path[-1]
        
        url = URL()
        
        if not path:
            url.path = str(URL(current).path)
        else:
            url.path = base if path.startswith('/') else controller
            url.path.append(path[1:] if path.startswith('/') else path)
        
        url.query = params
        url.fragment = anchor
        
        return str(url)


class Pager(object):
    def __init__(self, iterable, page, per, total=None):
        self.iterable = iterable
        self.page = page
        self.per = per
        
        try:
            self.total = total or len(iterable)
        except TypeError:
            self.total = None # indeterminate maximum
        
        self._iterable = iterable[self.slice]
    
    def __len__(self):
        try:
            return len(self._iterable)
        except TypeError:
            if self.total is None:
                return self.per
            else:
                return min(self.total, self.per)
    
    @property
    def count(self):
        return int(math.ceil(self.total / float(self.per)))
    
    def prev(self):
        return Pager(self.iterable, max(0, self.page - 1), self.per, self.total)
    
    def next(self):
        if self.total is not None:
            return Pager(self.iterable, self.page + 1, self.per, self.total)
        
        return Pager(self.iterable, min(len(self), self.page + 1), self.per, self.total)
    
    def __iter__(self):
        return self._iterable.__iter__()
    
    @property
    def slice(self):
        return slice(self.per * (self.page - 1), (self.per * self.page) - 1)
    
    def __getitem__(self, item):
        return self._iterable.__getitem__(item)
    
    def pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:
        """
        last = 0
        page = self.page
        pages = self.count
        for num in range(1, pages + 1):
            if num <= left_edge or \
               (num > page - left_current - 1 and \
                num < page + right_current) or \
               num > pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


if __name__ == '__main__':
    stuff = [1,2,3,4,5,6,7,8,9]
    p = Pager(stuff, 1, 2)
    
    print(p.page, p.per, p.total, p.count)
    print(len(p), p.slice)
    print(list(p.pages()))
    print(list(p))
