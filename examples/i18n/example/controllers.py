# encoding: utf-8
from datetime import datetime

from web.core import Controller, session
from web.core.locale import _, set_lang, LanguageError


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

        except LanguageError:
            return _("Invalid language selection.")

        return _("I now speak %(lingua)s.") % dict(lingua=lingua)

    def time(self):
        return 'example/templates/template.html', dict(now=datetime.now())
