# encoding: utf-8

# Standard Library Imports
from weakref import proxy
from functools import partial

# Third-Party Imports
from marrow.util.compat import basestring
from marrow.util.bunch import Bunch

# Local Imports
from web.core.response import registry
from web.ext.template.handler import template_handler, annotated_template_handler
from web.ext.template import render


class TemplateExtension(object):
    """Template rendering extension.
    
    Configuration:
    
        application:
            extensions:
                template:
                    default: mako
                    
                    # Optional configuration directives.
                    path: /path/to/use/for/relative/templates
                    override:
                        somepackage.somemodule: otherpackage.othermodule
    
    Setting a default means you won't need to prefix all of your template paths with an engine.  Remember, if you are
    writing a reusable component, *always* prefix your template paths with an engine!
    
    If you define a path here then relative templates (e.g. "mako:./welcome.html") will be relative to that path.
    Reusable components should never use relative paths.
    
    If you define an override mapping (whose values may be a string or list of strings) then templates for the given
    namespace will search there first.  For example:
    
        return 'mako:web.app.blog.templates.comments', dict()
    
    With the following override:
    
        override:
            web.app.blog: gothcandy
    
    The framework will try look for templates in this order:
    
    * gothcandy.templates.comments
    * web.app.blog.templates.comments
    
    Note that these overrides are prefix overrides, you can only replace from the beginning of the template path.
    
    Yes, you can also override the template engine, simply prefix your override value with the engine and a colon.
    """
    
    uses = ['locale']
    provides = ['template']
    
    class Namespace(object):
        def __contains__(self, name):
            return hasattr(self, name)
        
        def __iter__(self):
            return ((i, getattr(self, i)) for i in dir(self) if i[0] != '_')
    
    def __init__(self, default=None, path=None, override=None):
        """Executed to configure the extension."""
        super(TemplateExtension, self).__init__()
        
        if default and not hasattr(render._render, default):
            raise ValueError('"{0}" is not a valid engine, perhaps you need to install an adapter?'.format(default))
        
        render._render.default = default
        render.render.path = path
        
        if override:
            override = dict(override)  # we want a copy as a plain dictionary
            
            # Ensure that all single values become one-element lists.
            # Greatly simplifies the per-request code.
            for key in override:
                value = override[key]
                if isinstance(value, basestring):
                    override[key] = [value]
        
        render.render.overrides = override
    
    def start(self, context):
        """Register the template response handler."""
        registry.register(template_handler, tuple)
        registry.register(annotated_template_handler, dict)
        context.namespace = self.Namespace
    
    def prepare(self, context):
        context.namespace = context.namespace()
        context.namespace.web = proxy(context)
        context.render = partial(render.render, context)
