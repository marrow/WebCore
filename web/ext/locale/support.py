# encoding: utf-8

"""Multilingualization (m17n) utilities."""

from __future__ import unicode_literals, print_function

import os

try:
	from babel.core import Locale as Lingua, LOCALE_ALIASES
	from babel.support import Translations
except ImportError:
	print("Unable to find the babel package. To correct this, run: pip install babel")
	raise

from web.core import local
from web.core.compat import unicode, iterkeys


class L_(object):
	"""Lazy version of ugettext."""
	
	__slots__ = ('__message', )
	
	def __init__(self, message):
		self.__message = message
		super(L_, self).__init__()
	
	@property
	def __translated(self):
		return local.context.locale.catalog.ugettext(self.__message)
	
	def __add__(self, other):
		return self.__translated + other
	
	def __getattr__(self, name):
		return getattr(self.__translated, name)
	
	def __str__(self):
		return local.context.locale.catalog.gettext(self.__message)
	
	def __unicode__(self):
		return local.context.locale.catalog.ugettext(self.__message)
	
	if py3: # pragma: no cover
		__bytes__ = __str__
		__str__ = __unicode__
		del __unicode__


class Locale(object):
	"""Contextual locale.
	
	Acts as a domain/language cache.
	"""
	
	__slots__ = ('language', 'native', 'aliases', 'context', 'path', 'catalogs')
	
	def __init__(self, language, native='en_US', aliases=None, context=None):
		super(Locale, self).__init__()
		
		self.aliases = dict(LOCALE_ALIASES, **aliases) if aliases else LOCALE_ALIASES
		self.language = self.parse(language)
		self.native = self.parse(native)
		self.context = context
		
		self.path = []
		self.catalogs = {None: {}}
	
	@property
	def languages(self):
		return iterkeys(self.catalogs[None])
	
	def extend(self, paths):
		for path in paths:
			self.path.append(path)
			self._load_catalogs(path)
	
	def _load_catalog(self, domain, lang, fh):
		translations = Translations(fh, domain)
		lang = unicode(self.parse(lang))
		
		self.catalogs.setdefault(domain, {})
		
		if lang not in self.catalogs[domain]:
			self.catalogs[domain][lang] = translations
		else:
			self.catalogs[domain][lang].files = list(self.catalogs[domain][lang].files)  # Python 3 fix.
			self.catalogs[domain][lang].merge(translations)
		
		self.catalogs[None].setdefault(lang, Translations())
		self.catalogs[None][lang].files = list(self.catalogs[None][lang].files)  # Python 3 fix.
		self.catalogs[None][lang].merge(translations)
	
	def _load_catalogs(self, path):
		if path[0] in ('/', '.'):
			# Handle non-package-derived paths.
			requirement = None
			resource_listdir = lambda d, p: os.listdir(p)
			resource_isdir = lambda d, p: os.path.isdir(p)
			resource_exists = lambda d, p: os.path.exists(p)
			resource_stream = lambda d, p: open(p, 'rb')
		else:
			from pkg_resources import resource_listdir, resource_isdir, resource_exists, resource_stream
			requirement, _, path = path.partition('/')
		
		listing = list(resource_listdir(requirement, path or None))
		
		# First pass: catalogs at the same level.
		for name in (i for i in listing if i[-3:] == '.mo'):
			domain, _, lang = name[:-3].partition('-')
			self._load_catalog(domain, lang, resource_stream(requirement, path + '/' + name))
		
		# Second pass: catalogs in a nested structure.
		for lang in (i for i in listing if len(i) <= 5):  # Look for language directories.
			cpath = path + '/' + lang + '/LC_MESSAGES'
			if resource_isdir(requirement, cpath):
				for domain in (i[:-3] for i in resource_listdir(requirement, cpath) if i[-3:] == '.mo'):
					self._load_catalog(domain, lang, resource_stream(requirement, cpath + '/' + domain + '.mo'))
	
	def prepare(self, context):
		instance = self.__class__(self.language, self.native, self.aliases, context)
		
		instance.path = self.path
		instance.catalogs = self.catalogs
		
		return instance
	
	def parse(self, value):
		value = self.aliases.get(value, value)
		return Lingua.parse(value)
	
	def negotiate(self, want, have):
		return Lingua.negotiate(
				(unicode(self.parse(i)) for i in want),
				(unicode(self.parse(i)) for i in have)
			)
	
	def get(self, domain, lang=None, fallback=None):
		"""Get a translator object for the given domain.
		
		If `lang` is unspecified, defaults to the current language.  Only specify `fallback` if also explicitly
		selecting a language.
		"""
		value = self.catalogs[domain]
		fallback = fallback or self.native
		
		if lang:
			lang = unicode(self.parse(lang))
			if lang not in value:
				lang = unicode(self.parse(fallback))
			
			value = value[lang]
		
		return value
	
	def set(self, lang, domain=None):
		"""Set or change the currently selected language (and region)."""
		
		self.language = self.parse(lang)
	
	@property
	def catalog(self):
		return self.get(None, self.language)
