# encoding: utf-8

import web
from web.core import Controller, session
from web.core.i18n import _, set_lang



class RootController(Controller):
    def index(self):
        return _('Hello world!')
    
    def hello(self, name):
        return _("Hello, %(name)s!") % dict(name=name)
    
    def session(self, **kw):
        session.update(kw)
        session.save()
        
        return repr(session)
    
    def translate(self, lingua=None):
        try:
            set_lang(lingua)
        
        except web.core.i18n.LanguageError:
            return _("Invalid language selection.")
        
        return _("I now speak %(lingua)s.") % dict(lingua=lingua)
    
    def error(self):
        raise ValueError
    
    def time(self):
        from datetime import datetime
        return 'example/templates/template.html', dict(now=datetime.now())
