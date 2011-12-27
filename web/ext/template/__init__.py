# encoding: utf-8

from weakref import proxy
from functools import partial

from marrow.util.bunch import Bunch

from web.core.response import registry
from web.ext.template.handler import template_handler



class TemplateExtension(object):
    uses = ['locale']
    provides = ['template']
    
    def __init__(self, config):
        """Executed to configure the extension."""
        super(TemplateExtension, self).__init__()
    
    def start(self):
        """Executed during application startup just after binding the server."""
        
        # Register the template response handler.
        registry.register(template_handler, tuple)
    
    def prepare(self, context):
        from web.ext.template.render import render
        
        context.namespace = Bunch(web=proxy(context))
        context.render = partial(render, context)
