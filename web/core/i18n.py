"""Translation/Localization functions.

Provides :mod:`gettext` translation functions via an app's
``pylons.translator`` and get/set_lang for changing the language
translated to.

"""
import os
from gettext import NullTranslations, translation

import web
from web.extras.templating import registry
from web.core.middleware import middleware, defaultbool


__all__ = ['_', 'L_', 'add_fallback', 'get_lang', 'gettext', 'gettext_noop',
           'lazy_gettext', 'lazy_ngettext', 'lazy_ugettext', 'lazy_ungettext',
           'ngettext', 'set_lang', 'ugettext', 'ungettext', 'LanguageError',
           'N_', 'P_', 'get_translator']
__template_vars__ = ['_', 'L_', 'N_', 'P_']
log = __import__('logging').getLogger(__name__)


class LanguageError(Exception):
    """Exception raised when a problem occurs with changing languages"""
    pass


class LazyObject(object):
    """Allows you to lazily execute a wrapper function.
    
    Override the eval() method to produce the actual value.
    """
    
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def eval(self):
        return self.func(*self.args, **self.kwargs)
    
    def __getattr__(self, name):
        return getattr(self.eval(), name)


def lazify(func):
    """Decorator to return a lazy-evaluated version of the original"""
    def newfunc(*args, **kwargs):
        return LazyObject(func, *args, **kwargs)
    try:
        newfunc.__name__ = 'lazy_%s' % func.__name__
    except TypeError: # Python < 2.4
        pass
    newfunc.__doc__ = 'Lazy-evaluated version of the %s function\n\n%s' % \
        (func.__name__, func.__doc__)
    return newfunc


def gettext_noop(value):
    """Mark a string for translation without translating it. Returns
    value.

    Used for global strings, e.g.::

        foo = N_('Hello')

        class Bar:
            def __init__(self):
                self.local_foo = _(foo)

        h.set_lang('fr')
        assert Bar().local_foo == 'Bonjour'
        h.set_lang('es')
        assert Bar().local_foo == 'Hola'
        assert foo == 'Hello'

    """
    return value

N_ = gettext_noop


def gettext(value):
    """Mark a string for translation. Returns the localized string of
    value.

    Mark a string to be localized as follows::

        gettext('This should be in lots of languages')

    """
    return web.core.translator.gettext(value)

lazy_gettext = lazify(gettext)


def ugettext(value):
    """Mark a string for translation. Returns the localized unicode
    string of value.

    Mark a string to be localized as follows::

        _('This should be in lots of languages')
    
    """
    return web.core.translator.ugettext(value)

lazy_ugettext = lazify(ugettext)


def ngettext(singular, plural, n):
    """Mark a string for translation. Returns the localized string of
    the pluralized value.

    This does a plural-forms lookup of a message id. ``singular`` is
    used as the message id for purposes of lookup in the catalog, while
    ``n`` is used to determine which plural form to use. The returned
    message is a string.

    Mark a string to be localized as follows::

        ngettext('There is %(num)d file here', 'There are %(num)d files here',
                 n) % {'num': n}

    """
    return web.core.translator.ngettext(singular, plural, n)

lazy_ngettext = lazify(ngettext)


def ungettext(singular, plural, n):
    """Mark a string for translation. Returns the localized unicode
    string of the pluralized value.

    This does a plural-forms lookup of a message id. ``singular`` is
    used as the message id for purposes of lookup in the catalog, while
    ``n`` is used to determine which plural form to use. The returned
    message is a Unicode string.

    Mark a string to be localized as follows::

        ungettext('There is %(num)d file here', 'There are %(num)d files here',
                  n) % {'num': n}

    """
    return web.core.translator.ungettext(singular, plural, n)

lazy_ungettext = lazify(ungettext)
P_ = ungettext


def _(singular, plural=None, n=None):
    if plural and n:
        return ungettext(singular, plural, n)
    
    return ugettext(singular)

L_ = lazify(_)


def get_translator(lang, conf=None, **kwargs):
    """Utility method to get a valid translator object from a language name."""
    if not lang:
        return NullTranslations()
    
    if conf is None:
        conf = web.core.request.environ['paste.config']
    
    if not isinstance(lang, list):
        lang = [lang]
    
    try:
        translator = translation(conf['web.root.package'], conf['web.i18n.path'], languages=lang, **kwargs)
    
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
        
        # Determine langauge order.
        config['lang'] = [i.strip(' ,') for i in config.get('lang', 'en').split(',')]
        
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


@middleware('i18n', after="widgets")
def i18n(app, config):
    if not defaultbool(config.get('web.i18n', True), ['gettext']):
        return app
    
    return I18n(app, config)



# Register the appropriate i18n functions in the global template scope.
_ = dict()
for name in __template_vars__:
    _[name] = locals()[name]
registry.append(_)
