# encoding: utf-8

"""
"""


import                                          pkg_resources, web
from web.utils.object                           import DottedFileNameFinder


__all__ = ['TemplatingMiddleware']
log = __import__('logging').getLogger(__name__)

_engines = dict((_engine.name, _engine) for _engine in pkg_resources.iter_entry_points('python.templating.engines'))


class TemplatingMiddleware(object):
    def __init__(self, application, config=dict(), **kw):
        self.config = config.copy()
        self.config.update(kw)
        self.application = application
    
    def variables(self):
        return dict()
    
    def __call__(self, environ, start_response):
        # TODO: Set some environment variables to begin with.
        
        environ.update({
                'buffet.engine': self.config.get("buffet.engine", "genshi"),
                'buffet.options': self.config.get("buffet.options", dict()),
                'buffet.format': self.config.get("buffet.format", "html"),
                'buffet.fragment': self.config.get("buffet.fragment", False),
            })
        
        result = self.application(environ, start_response)
        
        # Bail if the returned value is not a tuple.
        if not isinstance(result, tuple): return result
        
        if len(result) == 2: template, data, extras = result + (dict(), )
        elif len(result) == 3: template, data, extras = result
        else: return result # We can't deal with this.
        
        if not isinstance(template, str) or not isinstance(data, dict) or not isinstance(extras, dict):
            raise TypeError("Invalid tuple values returned to TemplatingMiddleware.")
        
        # Determine the templating engine to use.
        # The template engine can be defined by, in order of presidence, the returned value, the environment, or the configuration.
        if ':' in template: template = template.split(':')
        engine = template[0] if isinstance(template, list) else environ.get("buffet.engine", "genshi")
        template = template[1] if isinstance(template, list) else template
        
        # Allocate a Buffet engine to handle this template request.
        # TODO: Cache the result of this based on the input of variable callback and options.
        
        options = self.config.get("buffet.%s.options" % (engine, ), dict())
        options.update(environ.get("buffet.options", dict()))
        options.update(extras)
        if 'buffet.format' in options: del options['buffet.format']
        if 'buffet.fragment' in options: del options['buffet.fragment']
        
        engine = _engines[engine].load()
        engine = engine(self.variables, options)
        
        del options
        
        result = engine.render(
                data,
                extras.get("buffet.format", environ.get("buffet.format", "html")),
                extras.get("buffet.fragment", environ.get("buffet.fragment", False)),
                template
            )
        
        if isinstance(result, str):
            web.core.response.body = result
        
        elif isinstance(result, unicode):
            web.core.response.unicode_body = result
        
        return web.core.response(environ, start_response)
        