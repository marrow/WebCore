# encoding: utf-8
from __future__ import unicode_literals

from web.core import Application
from web.core.locale import L_, N_, _, __, ugettext, gettext, ngettext, ungettext
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

    def placeholder(self):
        return N_('This works!')



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
    
    def test_placeholder(self):
        self.assertResponse('/placeholder', _environ=self.environ, body=b'This works!')
