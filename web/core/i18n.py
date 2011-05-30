"""Translation/Localization functions."""
from gettext import NullTranslations, translation
import os

from web.core.templating import registry
from web.core.middleware import middleware, defaultbool
import web


__all__ = ['LanguageError', '_', '__', 'L_', 'L__', 'N_', 'gettext',
           'ugettext', 'ngettext', 'ungettext', 'get_lang', 'set_lang',
           'get_translator', 'add_fallback']

log = __import__('logging').getLogger(__name__)


class LanguageError(Exception):
    """Exception raised when a problem occurs with changing languages"""
    pass


def gettext(self, message):
    return web.core.translator.gettext(message)


def ugettext(self, message):
    return web.core.translator.ugettext(message)


def ngettext(self, singular, plural, n):
    return web.core.translator.ngettext(singular, plural, n)


def ungettext(self, singular, plural, n):
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
        from nose.tools import set_trace; set_trace()
        return web.core.translator.ugettext(self.__message)

    def __add__(self, other):
        return self.__translated + other

    def __getattr__(self, name):
        return getattr(self.__translated, name)


class L__(object):
    """Lazy version of ungettext."""
    def __init__(self, singular, plural, n):
        self.__singular = singular
        self.__plural = plural
        self.__n = n

    def __getattr__(self, name):
        translated = web.core.translator.ungettext(self.__singular, self.__plural, self.__n)
        return getattr(translated, name)


def get_translator(lang, conf=None, **kwargs):
    """Utility method to get a valid translator object from a language name."""
    if not lang:
        return NullTranslations()

    if conf is None:
        conf = web.core.request.environ['paste.config']

    if not isinstance(lang, list):
        lang = [lang]

    try:
        translator = translation(conf['web.root.package'], conf['web.i18n.path'],
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


class I18n(object):
    def __init__(self, application, config=dict(), **kw):
        self.application = application
        self.config = config

        # Find the i18n folder, working from the package up to the root controller.
        path = config.get('web.i18n.path', None)

        if path is None:
            # Attempt to discover the path automatically.
            log.info(config['web.root'].__module__)

            module = __import__(config['web.root'].__module__)
            parts = config['web.root'].__module__.split('.')[1:]
            path = module.__file__

            while parts:
                # Search up the package tree, in case this is an application in a sub-module.

                path = os.path.abspath(path)
                path = os.path.dirname(path)
                path = os.path.join(path, 'i18n')

                log.debug("Trying %r", path)

                if os.path.isdir(path):
                    break

                module = getattr(module, parts.pop(0))
                path = module.__file__

        if not os.path.isdir(path):
            log.warn("Unable to find folder to store i18n strings.  Please specify web.i18n.path in your config.")
            raise Exception("Unable to find folder to store i18n strings.  Please specify web.i18n.path in your config.")

        config['web.i18n.path'] = path

        # Determine language order.
        config['lang'] = [i.strip(' ,') for i in config.get('lang', 'en').split(',')]

        # Register the appropriate i18n functions in the global template scope.
        registry.append({'_': _, '__': __, 'L_': L_, 'L__': L__, 'N_': N_})

        log.debug("Default language path: %r", config['lang'])

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
