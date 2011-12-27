# encoding: utf-8

from marrow.util.compat import basestring


def template_handler(context, result):
    if 2 > len(result) > 3:
        return False
    
    if len(result) == 2:
        template, data, extras = result + (dict(),)
    elif len(result) == 3:
        template, data, extras = result
        
    if not isinstance(template, basestring) or not isinstance(extras, dict):
        return False
    
    response = context.response
    mime, response.body = context.render(template, data, **extras)
    
    if response.mime is None:
        response.mime = mime
    
    return True
