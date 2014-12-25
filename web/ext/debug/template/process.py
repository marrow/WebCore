# encoding: utf-8

from __future__ import unicode_literals, print_function

import re
import tenjin

from tenjin.helpers import *


MESSAGE_CATALOG = dict(
	en = {
		'redirect.title':
			"Captured Redirect",
		
		'redirect.location':
			"Location:",
		
		'redirect.notice':
			"The debug toolbar has intercepted, for diagnostic purposes, a redirection to the above URL. You can click the above link to continue with the redirect as normal.",
	},
	
	fr = {
		'redirect.title':
			"Redirection capturée",
		
		'redirect.location':
			"Localisation :",
		
		'redirect.notice':
			"La barre d'outils débogage a intercepté, à des fins diagnostiques, une redirection vers l'URL ci-dessus. Vous pouvez cliquer sur le lien ci-dessus pour continuer avec la redirection comme d'habitude.",
	},
)


def create_m17n_func(lang):
	try:
		return MESSAGE_CATALOG[lang].get
	except KeyError:
		raise ValueError("%s: unknown lang." % lang)


if __name__ == '__main__':
	tenjin.set_template_encoding('utf-8')
	
	for lang in sorted(MESSAGE_CATALOG):
		engine = tenjin.Engine(
				preprocess = True,
				lang = lang,
				pp = [tenjin.TrimPreprocessor(True), tenjin.PrefixedLinePreprocessor()],
			)
		
		context = {'_': create_m17n_func(lang)}
		
		class Capture(object):
			status = '302 Found'
			location = '/other'
		
		context['capture'] = Capture()
		
		for template in ('redirect', 'base'):
			html = engine.render(template + '.pyhtml', context)
			print("-" * 72)
			print("Language:", lang)
			print("Template:", template, end="\n\n")
			print(html)
