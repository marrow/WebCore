# encoding: utf-8

"""Internationalization (i18n) functions."""

from __future__ import unicode_literals

import os
import web
import warnings

from web.core.compat import str, unicode

from gettext import NullTranslations, translation
from .util import LanguageError, Lingua


class Locale(object):
	"""Contextual locale.
	
	Acts as a domain/language cache.
	"""
	
	__slots__ = ('lang', 'native')
	
	def get(self, domain, lang=None, fallback=None):
		"""Get a translator object for the given domain.
		
		If `lang` is unspecified, defaults to the current language.  Only specify `fallback` if also explicitly
		selecting a language.
		"""
		pass
	
	def set(self, lang, fallback=None):
		"""Set or change the currently selected language."""
		pass


class LocaleExtension(object):
	"""WebCore localization (l10n) and internationalization (i18n), or multilingualization (m17n) extension.
	
	You may supply an initial `path` identifying the location of your translation catalogs, a default `domain` for
	messages not otherwise tagged with a domain, and a `native` language to use as a fallback.  The `native` option
	is most useful when interoperating with reusable components who are themselves internationalized.  (In this case
	best effort will be made; if messages are not available in this language the component's default language will
	be used.)
	
	Message catalog files can be stored in one of two directory structures:
	
	* Recommended light-weight structure for new projects and reusable components:
		* `{domain}.pot` - Source strings.
		* `{domain}-{lang}.mo` - Language-specific strings.
		* `{domain}-{lang}.po` - Optional compiled language-specific strings.
	
	* Classic structure.  Useful to group multiple domains by language.
		* `{domain}.pot`
		* `{lang}/LC_MESSAGES/{domain}.mo`
		* `{lang}/LC_MESSAGES/{domain}.po`
	
	Search paths may be specified using the following notations:
	
	* `./relative/path` or `/absolute/path`
	* `package.specific`
	* `package.relative/path`
	
	A `locale` attribute is added to the context and provides access to the common translation functions for the
	current locale, a means of getting and setting the current locale, as well as a method for registering new
	search paths.  Thread locals are utilized to implement lazy string translation.
	
	If a domain exists in multiple paths the first instance will be used.
	"""
	
	__slots__ = ('path', 'native')
	
	uses = ['template', 'session']
	provides = ['i18n', 'internationalization', 'translation']
	
	def __init__(self, path=None, domain='messages', native='en_US'):
		"""Executed to configure the extension."""
		
		self.path = []  # Search path.
		
		if path:
			if isinstance(path, (str, unicode)):
				self.path.append(path)
			else:
				self.path.extend(path)
		
		super(LocaleExtension, self).__init__()
	
	def start(self, context):
		"""Executed during application startup just after binding the server."""
		
		context.locale = Locale(self.path)
	
	def prepare(self, context):
		"""Detect the current langauge and register the appropriate i18n functions in the global template scope."""
		
		
		
		if 'namespace' not in context:
			return
		
		# Populate the template namespace with our helper functions.
		for i in ('_', '__', 'L_', 'N_'):
			setattr(context.namespace, i, getattr(translator, i))
