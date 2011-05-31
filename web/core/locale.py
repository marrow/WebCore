# encoding: utf-8

"""Internationalization (i18n) functions."""

from gettext import NullTranslations, translation
import os

from paste.deploy.converters import aslist
from web.core.templating import registry
import web


__all__ = ['LanguageError', '_', '__', 'L_', 'N_', 'gettext',
           'ugettext', 'ngettext', 'ungettext', 'get_lang', 'set_lang',
           'get_translator', 'add_fallback']

log = __import__('logging').getLogger(__name__)


class LanguageError(Exception):
    """Exception raised when a problem occurs with changing languages"""
    pass


def gettext(message):
    return web.core.translator.gettext(message)


def ugettext(message):
    return web.core.translator.ugettext(message)


def ngettext(singular, plural, n):
    return web.core.translator.ngettext(singular, plural, n)


def ungettext(singular, plural, n):
    return web.core.translator.ungettext(singular, plural, n)


def N_(message):
    return message

_ = ugettext
__ = ungettext


class L_(object):
    """Lazy version of ugettext."""
    def __init__(self, message):
        self.__message = message

    @property
    def __translated(self):
        return web.core.translator.ugettext(self.__message)

    def __add__(self, other):
        return self.__translated + other

    def __getattr__(self, name):
        return getattr(self.__translated, name)


def get_translator(lang, conf=None, **kwargs):
    """Utility method to get a valid translator object from a language name."""
    if not lang:
        return NullTranslations()

    if conf is None:
        conf = web.core.request.environ['paste.config']

    if not isinstance(lang, list):
        lang = [lang]

    try:
        translator = translation(conf['web.locale.domain'], conf['web.locale.path'],
                                 languages=lang, **kwargs)

    except IOError, ioe:
        raise LanguageError('IOError: %s' % ioe)

    translator.lang = lang

    return translator


def set_lang(lang, **kwargs):
    """Set the current language used for translations.
    
    ``lang`` should be a string or a list of strings. If a list of
    strings, the first language is set as the main and the subsequent
    languages are added as fallbacks.
    
    If ``lang`` is None, the override will be removed from the session.
    """

    if lang is None:
        if web.core.request.environ.has_key('beaker.session') and 'lang' in web.core.session:
            del web.core.session['lang']
            web.core.session.save()

        return

    translator = get_translator(lang, **kwargs)
    web.core.request.environ['paste.registry'].replace(web.core.translator, translator)

    if web.core.request.environ.has_key('beaker.session'):
        web.core.session['lang'] = translator.lang
        web.core.session.save()


def get_lang():
    """Return a list of the currently selected languages, in priority order."""
    return getattr(web.core.translator, 'lang', None)


def add_fallback(lang, **kwargs):
    """Add a fallback language from which words not matched in other
    languages will be translated to.

    This fallback will be associated with the currently selected
    language -- that is, resetting the language via set_lang() resets
    the current fallbacks.

    This function can be called multiple times to add multiple
    fallbacks.
    """
    return web.core.translator.add_fallback(get_translator(lang, **kwargs))


class LocaleMiddleware(object):
    def __init__(self, application, config=dict(), **kw):
        self.application = application
        self.config = config

        localedir = self._find_locale_dir()
        log.info("Locale directory: %s", localedir)

        domain = self._find_text_domain(localedir)
        log.info("Text domain for translations: %s", domain)

        languages = self._find_translations(localedir, domain)
        log.info("Supported languages: %r", languages)

        # Register the appropriate i18n functions in the global template scope.
        registry.append({'_': _, '__': __, 'L_': L_, 'N_': N_})

    def _find_locale_dir(self):
        # Locate the directory that contains the top level package
        root_controller = self.config['web.root']
        root_parts = root_controller.__module__.split('.')
        root_module = __import__(root_controller.__module__)
        root_path = os.path.dirname(root_module.__file__)
        steps = len(root_parts)
        if not os.path.split(root_path)[1].startswith('__init__.'):
            steps -= 1
        for _ in range(steps):
            root_path = os.path.split(root_path)[0]

        if 'web.locale.path' in self.config:
            # Validate the pre-defined locale path
            path = self.config['web.locale.path']
            if not os.path.abspath(path) == os.path.normpath(path):
                path = os.path.join(root_path, path)
            if not os.path.isdir(path):
                raise Exception("The locale path (%s) either does not exist or is not a directory." % path)
            return path

        # Autodetect the locale path
        path = root_path
        for part in root_parts:
            path = os.path.join(path, part)
            localedir = os.path.join(path, 'locale')
            log.debug("Looking for directory 'locale' in %s", localedir)
            if os.path.isdir(localedir):
                self.config['web.locale.path'] = localedir
                return localedir
        raise Exception("Unable to autodetect the locale directory. Please set web.locale.path manually.")

    def _find_text_domain(self, localedir):
        # Allow users to override
        if 'web.locale.domain' in self.config:
            return self.config['web.locale.domain']

        for _path, _dirs, files in os.walk(localedir, topdown=False):
            mofiles = [f for f in files if os.path.splitext(f)[1] == '.mo']
            if len(mofiles) == 1:
                self.config['web.locale.domain'] = mofiles[0][:-3]
                return self.config['web.locale.domain']
            if len(mofiles) > 1:
                raise Exception("More than one text domain found -- please set web.locale.domain manually.")

        raise Exception('No .mo files found -- cannot determine the text domain.')

    def _find_translations(self, localedir, domain):
        # Allow users to override
        if 'web.locale.languages' in self.config:
            return aslist(self.config['web.locale.languages'])

        translations = []
        for fname in os.listdir(localedir):
            mo_fname = os.path.join(localedir, fname, 'LC_MESSAGES', '%s.mo' % domain)
            if os.path.exists(mo_fname):
                translations.append(fname)
        return translations

    def __call__(self, environ, start_response):
        lang = []
        lang.extend(environ.get('beaker.session', dict()).get('lang', []))

        for i in environ.get('HTTP_ACCEPT_LANGUAGE', '').split(','):
            i = i.strip(', ')
            i = i.split(';', 1)[0]
            lang.append(i)
            if '-' in i:
                lang.append(i.split('-', 1)[0])

        lang.extend(environ['paste.config'].get('lang', ['en']))

        log.debug("Call language path: %r", lang)

        translator = get_translator(lang, self.config)
        environ['web.translator'] = translator
        environ['paste.registry'].register(web.core.translator, translator)

        return self.application(environ, start_response)
