# encoding: utf-8

from marrow.util.compat import basestring


def template_handler(context, result):
    if 2 > len(result) > 3:
        raise TypeError("Invalid tuple returned: invalid length.")
    
    if len(result) == 2:
        template, data, extras = result + (dict(),)
    elif len(result) == 3:
        template, data, extras = result
        
    if not isinstance(template, basestring) or not isinstance(extras, dict):
        raise TypeError("Invalid tuple values returned to TemplatingMiddleware.")
    
    response = context.response
    mime, response.body = context.render(template, data, **extras)
    
    if response.mime is None:
        response.mime = mime
