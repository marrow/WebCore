# encoding: utf-8

"""
"""


import pkg_resources

import web
from web.utils.object import DottedFileNameFinder
from web.utils.dictionary import adict


__all__ = ['template', 'TemplatingMiddleware']
log = __import__('logging').getLogger(__name__)

_engines = dict((_engine.name, _engine) for _engine in pkg_resources.iter_entry_points('python.templating.engines'))
_lookup = DottedFileNameFinder()



def template(template, **extras):
    def outer(func):
        def inner(*args, **kw):
            return TemplatingMiddleware.render(template, func(*args, **kw), **extras)
        
        # Become more transparent.
        inner.__name__ = func.__name__
        inner.__doc__ = func.__doc__
        inner.__dict__ = func.__dict__
        inner.__module__ = func.__module__
        
        return inner
    return outer


class TemplatingMiddleware(object):
    def __init__(self, application, config=dict(), **kw):
        self.config = config.copy()
        self.config.update(kw)
        self.application = application
    
    @classmethod
    def variables(cls):
        def lookup(template_name, template_extension='.html'):
            return _lookup.get_dotted_filename(template_name, template_extension)
        
        return dict(
                web=adict(
                        request = web.core.request,
                        response = web.core.response,
                        session = web.core.session
                    ),
                lookup = lookup,
            )
    
    @classmethod
    def render(cls, template, data, **kw):
        # Determine the templating engine to use.
        # The template engine can be defined by, in order of presidence, the returned value, the environment, or the configuration.
        if ':' in template: template = template.split(':')
        engine = template[0] if isinstance(template, list) else web.core.request.environ.get("buffet.engine", "genshi")
        template = template[1] if isinstance(template, list) else template
        
        # Allocate a Buffet engine to handle this template request.
        # TODO: Cache the result of this based on the input of variable callback and options.
        
        options = web.core.request.environ.get("buffet.options", dict())
        options.update(kw)
        
        if 'buffet.format' in options: del options['buffet.format']
        if 'buffet.fragment' in options: del options['buffet.fragment']
        
        if template == 'json':
            try:
                from json import dumps
            except ImportError:
                from simplejson import dumps
            
            web.core.response.content_type = 'application/json; charset=utf-8'
            return dumps(data, **options)
        
        elif template == 'bencode':
            from web.extras.bencode import EnhancedBencode
            engine = EnhancedBencode()
            
            web.core.response.content_type = 'application/x-bencode; charset=utf-8'
            return engine.encode(data)
        
        engine = _engines[engine].load()
        engine = engine(cls.variables, options)
        
        del options
        
        return engine.render(
                data,
                kw.get("buffet.format", web.core.request.environ.get("buffet.format", "html")),
                kw.get("buffet.fragment", web.core.request.environ.get("buffet.fragment", False)),
                template
            )
    
    @classmethod
    def response(cls, result, environ, start_response):
        if isinstance(result, str):
            web.core.response.body = result
        
        elif isinstance(result, unicode):
            web.core.response.unicode_body = result
        
        return web.core.response(environ, start_response)
    
    def __call__(self, environ, start_response):
        environ.update({
                'buffet.engine': self.config.get("buffet.engine", "genshi"),
                'buffet.options': self.config.get("buffet.options", dict()),
                'buffet.format': self.config.get("buffet.format", "html"),
                'buffet.fragment': self.config.get("buffet.fragment", False),
            })
        
        result = self.application(environ, start_response)
        
        # Bail if the returned value is not a tuple.
        if not isinstance(result, tuple):
            return result
        
        if len(result) == 2: template, data, extras = result + (dict(), )
        elif len(result) == 3: template, data, extras = result
        
        if not isinstance(template, str) or not isinstance(data, dict) or not isinstance(extras, dict):
            raise TypeError("Invalid tuple values returned to TemplatingMiddleware.")
        
        return self.response(self.render(template, data, **extras), environ, start_response)
