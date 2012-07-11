# encoding: utf-8

from weakref import proxy
from functools import partial

from marrow.util.bunch import Bunch

from web.core.response import registry
from web.ext.template.handler import template_handler, annotated_template_handler

from web.ext.template import render



class TemplateExtension(object):
    """Template rendering extension.
    
    web.template:
        engine: mako
        path: {...}
    
    """
    uses = ['locale']
    provides = ['template']
    
    def __init__(self, config):
        """Executed to configure the extension."""
        super(TemplateExtension, self).__init__()
        
        self.path = config.get('path', None)
        render._render.default = config.get('engine', None)
    
    def start(self):
        """Register the template response handler."""
        registry.register(template_handler, tuple)
        registry.register(annotated_template_handler, dict)
    
    def prepare(self, context):
        context.namespace = Bunch(web=proxy(context))
        context.render = partial(render.render, context)
        context.render.path = self.path
