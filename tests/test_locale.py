# encoding: utf-8
from __future__ import unicode_literals

import web.core

from gettext import NullTranslations
from web.core import Application
from web.core.locale import L_, N_, _, __, ugettext, gettext, ngettext, ungettext, get_translator, set_lang, get_lang
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

    def set_lang(self, l=None):
        set_lang(l)
        return gettext('This works!')

    def get_lang(self):
        return ','.join(get_lang())

    def cookies(self):
        return 'json:', web.core.request.headers.get('Cookie', "")

    def sid(self):
        return web.core.session.id


test_config = {'debug': True, 'web.locale.i18n': True, 'web.locale.fallback': 'fr', 'web.sessions': True,
        'web.sessions.type': 'memory', 'web.sessions.validate_key': 'a', 'web.sessions.auto': True}


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


class TestI18nSession(WebTestCase):
    app = Application.factory(root=RootController, **test_config)
    environ = {'HTTP_ACCEPT_LANGUAGE': 'fi, en-US, en'}

    def test_session(self):
        # print "\n>>>", self._cookies
        # resp = self.assertResponse('/cookies', _environ=self.environ, content_type='application/json')
        # print "<<<", resp.body
        # print "<<<", resp.headers.getall('Set-Cookie')

        resp1 = self.assertResponse('/sid', _environ=self.environ)
        resp2 = self.assertResponse('/sid', _environ=self.environ)
        self.assertEqual(resp1.body, resp2.body)

    def test_set_lang(self):
        self.assertResponse('/get_lang', _environ=self.environ, body='fi,en-US,en,en,fr')
        self.assertResponse('/set_lang?l=en', _environ=self.environ, body='This works!')
        self.assertResponse('/gettext', _environ=self.environ, body='This works!'.encode('utf-8'))
        self.assertResponse('/get_lang', _environ=self.environ, body='en,fi,en-US,en,en,fr')
        self.assertResponse('/set_lang?l=fi', _environ=self.environ, body='Tämä toimii!'.encode('utf-8'))
        self.assertResponse('/gettext', _environ=self.environ, body='Tämä toimii!'.encode('utf-8'))
        self.assertResponse('/get_lang', _environ=self.environ, body='fi,fi,en-US,en,en,fr')

    def test_set_lang_default(self):
        self.assertResponse('/get_lang', _environ=self.environ, body='fi,en-US,en,en,fr')
        self.assertResponse('/set_lang?l=en', _environ=self.environ, body='This works!')
        self.assertResponse('/gettext', _environ=self.environ, body='This works!'.encode('utf-8'))
        self.assertResponse('/get_lang', _environ=self.environ, body='en,fi,en-US,en,en,fr')
        self.assertResponse('/set_lang', _environ=self.environ, body='Tämä toimii!'.encode('utf-8'))
        self.assertResponse('/gettext', _environ=self.environ, body='Tämä toimii!'.encode('utf-8'))
        self.assertResponse('/get_lang', _environ=self.environ, body='fi,en-US,en,en,fr')
