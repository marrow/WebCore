# encoding: utf-8

"""Multilingualization Extension

Providing internationalization (translation) and localization (region formatting) services for your application,
extensions, and reusable components.

Context Additions: locale

# Introduction

## Purpose

## Requirements

### Python Packages

* [babel]()

### Message Catalogs

## Operation

# Usage

## Configuration

## Internationalization

### Use in Python Code

### Use in Templates

### Lazy Evaluation

## Localization

## Managing Message Catalogs


# Old Docs

You may supply an initial `path` identifying the location of your translation catalogs, a default `domain` for
messages not otherwise tagged with a domain, and a `native` language to use as a fallback.  The `native` option
is most useful when interoperating with reusable components who are themselves internationalized.  (In this case
best effort will be made; if messages are not available in this language the component's default language will
be used.)

Message catalog files can be stored in one of two directory structures:

* Recommended light-weight structure for new projects and reusable components:
	* `{domain}.pot` - Source strings.
	* `{domain}-{lang}.po` - Language-specific strings.
	* `{domain}-{lang}.mo` - Optional compiled language-specific strings.
	
* Classic structure.  Useful to group multiple domains by language:
	* `{domain}.pot`
	* `{lang}/LC_MESSAGES/{domain}.po`
	* `{lang}/LC_MESSAGES/{domain}.mo`

Search paths may be specified using the following notations:

* `./relative/path` or `/absolute/path`
* `package.specific`
* `package.relative/path`

A `locale` attribute is added to the context and provides access to the common translation functions for the
current locale, a means of getting and setting the current locale, as well as a method for registering new
search paths.  Thread locals are utilized to implement lazy string translation.

If a domain exists in multiple paths the first instance will be used.

You can extract messages from your code and templates and compile them by installing Babel and running:

* `web locale extract` - Extract messages.
* `web locale update` - Update `.po` message catalogs.
* `web locale compile` - Compile `.po` catalogs into `.mo` high-efficiency ones.

"""

from __future__ import unicode_literals, print_function

from web.core import local
from web.core.compat import unicode

from .support import Locale, L_


class LocaleExtension(object):
	__slots__ = ('locale', )
	
	needs = ['threadlocal']
	uses = ['template', 'session']
	provides = ['translation', 'm17n', 'multilingualization', 'l10n', 'localization', 'i18n', 'internationalization']
	
	def __init__(self, path=None, domain='messages', native='en_US', alias=None):
		"""Executed to configure the extension."""
		
		locale = self.locale = Locale(native, native, alias)
		
		if path:
			locale.path.extend([path] if isinstance(path, (str, unicode)) else path)
		
		super(LocaleExtension, self).__init__()
	
	def start(self, context):
		"""Executed during application startup just after binding the server."""
		
		# This constructs a context-bound Locale instance.  The context here is the class, not instance.
		context.locale = self.locale.prepare(context)
		
		if 'namespace' not in context:
			return
		
		context.namespace['_'] = lambda s: local.context.locale.catalog.ugettext(s)
		context.namespace['__'] = lambda s, p, n: local.context.locale.catalog.ungettext(s, p, n)
		context.namespace['L_'] = L_
		context.namespace['N_'] = lambda s: s
	
	def prepare(self, context):
		"""Detect the current langauge and register the appropriate i18n functions in the global template scope."""
		
		# This constructs a context-bound Locale instance.  The context here is a request-local instance of Context.
		locale = context.locale = context.locale.prepare(context)
		
		if 'session' in context and 'lang' in context.session:
			lang = context.session['lang']
		
		else:  # No explicit language selected, so we try to detect.
			candidates = []
			candidates.extend(unicode(self.parse(i[0].replace('-', '_'))) for i in context.request.accept_lang._parsed)
			candidates.append(unicode(self.native))
			lang = locale.negotiate(locale.languages, candidates)
		
		locale.set(lang)
		
		if 'namespace' not in context:
			return
		
		# Populate the template namespace with our helper functions.
		for i in ('_', '__', 'L_', 'N_'):
			setattr(context.namespace, i, getattr(translator, i))
