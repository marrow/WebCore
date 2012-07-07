# encoding: utf-8

"""Internationalization (i18n) functions."""

import os
import web
import warnings

from gettext import NullTranslations, translation
from web.core.templating import registry
from marrow.util.convert import array


__all__ = [
        'LanguageError', '_', '__', 'L_', 'N_', 'gettext', 'ugettext', 'ngettext', 'ungettext', 'get_lang', 'set_lang',
        'get_translator'
    ]

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

    def __str__(self):
        return web.core.translator.gettext(self.__message)

    def __unicode__(self):
        return web.core.translator.ugettext(self.__message)


def get_translator(lang, conf=None, **kwargs):
    """Utility method to get a valid translator object from a language name."""
    if not lang:
        return NullTranslations()

    if conf is None:
        conf = web.core.request.environ['paste.config']

    if not isinstance(lang, list):
        lang = [lang]

    domain = conf.get('web.locale.domain') or conf['web.root.package']
    try:
        translator = translation(domain, conf['web.locale.path'], languages=lang, **kwargs)
    except IOError as ioe:  # pragma: no cover
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

    session = web.core.request.environ.get('beaker.session')
    if lang is None:
        if session and 'lang' in session:
            del session['lang']
            session.save()

        lang = LocaleMiddleware.parse_linguas(web.core.request.environ)
        session = None

    translator = get_translator(lang, **kwargs)
    web.core.request.environ['paste.registry'].replace(web.core.translator, translator)

    if session:
        session['lang'] = translator.lang
        session.save()


def get_lang():
    """Return a list of the currently selected languages, in priority order."""
    return getattr(web.core.translator, 'lang', None)


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

        if 'web.i18n.path' in self.config:
            warnings.warn("The 'web.i18n.path' directive should be named 'web.locale.path'.\n"
                    "Please change your configuration accordingly for compatibility with future versions.",
                    DeprecationWarning)
            self.config['web.locale.path'] = self.config['web.i18n.path']

        if 'web.locale.path' in self.config: # pragma: no cover
            # Validate the pre-defined locale path
            path = self.config['web.locale.path']

            if not os.path.abspath(path) == os.path.normpath(path):
                path = os.path.join(root_path, path)

            if not os.path.isdir(path):
                raise ValueError("The locale path (%s) either does not exist or is not a directory." % path)

            return path

        # Look for the "locale" directory along the path to the root controller's package
        for dirname in 'locale', 'i18n':
            path = root_path
            for part in [''] + root_parts[1:]:
                path = os.path.join(path, part)
                localedir = os.path.join(path, dirname)
                log.debug("Looking for directory '%s' in %s", dirname, path)

                if os.path.isdir(localedir):
                    if dirname == 'i18n':
                        warnings.warn("The 'i18n' directory should be named 'locale'.\n"
                                "Please rename the directory accordingly for compatibility with future versions.",
                                DeprecationWarning)
                    self.config['web.locale.path'] = localedir
                    return localedir

        raise Exception("Unable to autodetect the locale directory. Please set web.locale.path manually.") # pragma: no cover

    def _find_text_domain(self, localedir):
        # Allow users to override
        if 'web.locale.domain' in self.config: # pragma: no cover
            return self.config['web.locale.domain']

        for _path, _dirs, files in os.walk(localedir, topdown=False):
            mofiles = [f for f in files if os.path.splitext(f)[1] == '.mo']

            if len(mofiles) == 1:
                self.config['web.locale.domain'] = mofiles[0][:-3]
                return self.config['web.locale.domain']

            if len(mofiles) > 1: # pragma: no cover
                raise Exception("More than one text domain found -- please set web.locale.domain manually.")

        raise Exception('No .mo files found -- cannot determine the text domain.') # pragma: no cover

    def _find_translations(self, localedir, domain):
        # Allow users to override
        if 'web.locale.languages' in self.config: # pragma: no cover
            return array(self.config['web.locale.languages'])

        translations = []
        for fname in os.listdir(localedir):
            mo_fname = os.path.join(localedir, fname, 'LC_MESSAGES', '%s.mo' % domain)

            if os.path.exists(mo_fname):
                translations.append(fname)

        return translations

    @classmethod
    def parse_linguas(cls, environ):
        languages = []
        languages.extend(environ.get('beaker.session', {}).get('lang', []))

        for i in environ.get('HTTP_ACCEPT_LANGUAGE', '').split(','):
            i = i.strip(', ')
            i = i.split(';', 1)[0]
            languages.append(i)

            if '-' in i:
                languages.append(i.split('-', 1)[0])

        languages.append(environ['paste.config'].get('web.locale.fallback', 'en'))
        return languages

    def __call__(self, environ, start_response):
        languages = self.parse_linguas(environ)
        log.debug("Call language path: %r", languages)

        translator = get_translator(languages, self.config)
        environ['web.translator'] = translator
        environ['paste.registry'].register(web.core.translator, translator)

        return self.application(environ, start_response)
