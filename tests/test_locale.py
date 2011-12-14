# encoding: utf-8
from __future__ import unicode_literals

from gettext import NullTranslations
from web.core import Application
from web.core.locale import L_, N_, _, __, ugettext, gettext, ngettext, ungettext, get_translator, set_lang
from common import PlainController, WebTestCase


class RootController(PlainController):
    lazy_message = L_('This works!')

    def gettext(self):
        return gettext('This works!')
    
    def ugettext(self):
        return ugettext('This works!')
    
    def ugettext_alt(self):
        return _('This works!')

    def ngettext(self, n):
        return ngettext('Singular works!', 'Plural works!', int(n))
    
    def ungettext(self, n):
        return ungettext('Singular works!', 'Plural works!', int(n))
    
    def ungettext_alt(self, n):
        return __('Singular works!', 'Plural works!', int(n))

    def lazy(self):
        return str(self.lazy_message)

    def lazy_unicode(self):
        return unicode(self.lazy_message)

    def lazy_append(self):
        return self.lazy_message + ' extra'

    def lazy_upper(self):
        return self.lazy_message.upper()

    def placeholder(self):
        return N_('This works!')

    def set_lang(self):
        set_lang('en')
        return gettext('This works!')


test_config = {'debug': True, 'web.locale.i18n': True}

class TestI18n(WebTestCase):
    app = Application.factory(root=RootController, **test_config)
    environ = {'HTTP_ACCEPT_LANGUAGE': 'fi, en-US, en'}

    def test_gettext(self):
        self.assertResponse('/gettext', _environ=self.environ, body='Tämä toimii!'.encode('utf-8'))

    def test_ugettext(self):
        self.assertResponse('/ugettext', _environ=self.environ, body='Tämä toimii!'.encode('utf-8'))

    def test_ngettext_1(self):
        self.assertResponse('/ngettext?n=1', _environ=self.environ, body='Yksikkö toimii!'.encode('utf-8'))

    def test_ngettext_2(self):
        self.assertResponse('/ngettext?n=2', _environ=self.environ, body='Monikko toimii!'.encode('utf-8'))

    def test_ungettext_1(self):
        self.assertResponse('/ungettext?n=1', _environ=self.environ, body='Yksikkö toimii!'.encode('utf-8'))

    def test_ungettext_2(self):
        self.assertResponse('/ungettext?n=2', _environ=self.environ, body='Monikko toimii!'.encode('utf-8'))

    def test_ungettext_alt(self):
        self.assertResponse('/ungettext?n=1', _environ=self.environ, body='Yksikkö toimii!'.encode('utf-8'))

    def test_lazy(self):
        self.assertResponse('/lazy', _environ=self.environ, body='Tämä toimii!'.encode('utf-8'))

    def test_lazy_unicode(self):
        self.assertResponse('/lazy_unicode', _environ=self.environ, body='Tämä toimii!'.encode('utf-8'))

    def test_lazy_append(self):
        self.assertResponse('/lazy_append', _environ=self.environ, body='Tämä toimii! extra'.encode('utf-8'))

    def test_lazy_upper(self):
        self.assertResponse('/lazy_upper', _environ=self.environ, body='TÄMÄ TOIMII!'.encode('utf-8'))
    
    def test_placeholder(self):
        self.assertResponse('/placeholder', _environ=self.environ, body='This works!')

    def test_get_null_translations(self):
        tr = get_translator(None, {})
        assert isinstance(tr, NullTranslations)

    def test_set_lang(self):
        self.assertResponse('/set_lang', _environ=self.environ, body='This works!')
