#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import os
import sys
import codecs


try:
	from setuptools.core import setup, find_packages
except ImportError:
	from setuptools import setup, find_packages


if sys.version_info < (2, 7):
	raise SystemExit("Python 2.7 or later is required.")
elif sys.version_info > (3, 0) and sys.version_info < (3, 2):
	raise SystemExit("CPython 3.3 or Pypy 3 (3.2) or later is required.")

version = description = url = author = author_email = ""  # Silence linter warnings.
exec(open(os.path.join("web", "core", "release.py")).read())  # Actually populate those values.

here = os.path.abspath(os.path.dirname(__file__))

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-capturelog',  # log capture
		'web.dispatch.object',  # dispatch tests
		'backlash',  # debug tests
	]


# ## Package Metadata

setup(
	# ### Basic Metadata
	name = "WebCore",
	version = version,
	description = description,
	long_description = codecs.open(os.path.join(here, 'README.rst'), 'r', 'utf8').read(),
	url = url,
	download_url = 'https://github.com/marrow/WebCore/releases',
	author = author.name,
	author_email = author.email,
	license = 'MIT',
	keywords = ['marrow', 'web.core', 'web.ext'],
	classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Environment :: Console",
			"Environment :: Web Environment",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Programming Language :: Python :: 2",
			"Programming Language :: Python :: 2.7",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.2",
			"Programming Language :: Python :: 3.3",
			"Programming Language :: Python :: 3.4",
			"Programming Language :: Python :: 3.5",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
			"Topic :: Internet :: WWW/HTTP :: WSGI",
			"Topic :: Software Development :: Libraries",
			"Topic :: Software Development :: Libraries :: Application Frameworks",
			"Topic :: Software Development :: Libraries :: Python Modules",
		],
	# As yet unsupported by setuptools.
	#document_names = {
	#		"description": "README.rst",
	#		"license": "LICENSE.txt",
	#	},
	#contacts = [
	#		{"name": "Alice Bevan-McGregor", "email": "alice@gothcandy.com", "role": "author"},
	#	],
	#project_urls = {
	#		"Documentation": "http://pythonhosted.org/WebCore/",
	#		"Home": "https://github.com/marrow/WebCore/",
	#		"Repository": "https://github.com/marrow/WebCore/",
	#		"Tracker": "https://github.com/marrow/WebCore/issues",
	#	},
	#environments = [
	#		"python_version >= '3.2'",
	#		"'3.0' > python_version >= '2.7'",
	#	],
	
	# ### Code Discovery
	
	packages = find_packages(exclude=['bench', 'docs', 'example', 'test', 'htmlcov']),
	include_package_data = True,
	namespace_packages = [
			'web',  # primary namespace
			'web.app',  # application code goes here
			'web.ext',  # framework extensions
			'web.server',  # front-end WSGI bridges
		],
	zip_safe = True,
	
	# ### Plugin Registration
	
	entry_points = {
			# #### Re-usable applications or application components.
			'web.app': [
					'static = web.app.static:static',
				],
			
			'web.acl.predicate': [
					'not = web.ext.acl:Not',
					'always = web.ext.acl:always',
					'never = web.ext.acl:never',
					'first = web.ext.acl:First',
					'all = web.ext.acl:all',
					'any = web.ext.acl:any',
					'matches = web.ext.acl:ContextMatch',
					'contains = web.ext.acl:ContextContains',
				],
			
			# #### WebCore Extensions
			'web.extension': [
					# ##### BaseExtension, providing request, response, and default views.
					'base = web.ext.base:BaseExtension',
					'request = web.ext.base:BaseExtension',
					'response = web.ext.base:BaseExtension',
					
					# ##### Miscelaneous Builtin Extensions
					'acl = web.ext.acl:ACLExtension',  # Access control list validation.
					'analytics = web.ext.analytics:AnalyticsExtension',
					'annotation = web.ext.annotation:AnnotationExtension',  # Preferred use/needs reference.
					'cast = web.ext.annotation:AnnotationExtension',  # Legacy reference.
					'db = web.ext.db:DBExtension',  # Database Connection Management
					'typecast = web.ext.annotation:AnnotationExtension',  # Legacy reference.
					'local = web.ext.local:ThreadLocalExtension',  # Preferred use/needs reference.
					'threadlocal = web.ext.local:ThreadLocalExtension',  # Legacy reference.
					'assets = web.ext.assets:WebAssetsExtension',  # WebAssets integration.
				],
			
			# #### WSGI Server Adapters
			'web.server': [
					# These are built-in to Python itself, but are reference implementations. Do not rely on these in
					# production environments; a warning will be issued on attempts to use these if optimizations are
					# enabled.
					'wsgiref = web.server.stdlib:simple',
					'cgiref = web.server.stdlib:cgi',
					'iiscgiref = web.server.stdlib:iiscgi',  # Python 3 only!
					
					# These have additional third-party dependencies.
					# For even more, see the WSGI reference site listing of servers:
					# http://wsgi.readthedocs.org/en/latest/servers.html)
					'waitress = web.server.waitress_:serve[waitress]',  # http://s.webcore.io/aIou
					'tornado = web.server.tornado_:serve[tornado]',  # http://s.webcore.io/aIaN
					'fcgi = web.server.fcgi:serve[flup]',  # http://s.webcore.io/fhVY
					'cherrypy = web.server.cherrypy_:serve[cherrypy]',  # http://s.webcore.io/aIoF
					'appengine = web.server.appengine:serve',  # http://s.webcore.io/aIic
					'paste = paste.httpserver:serve[paste]',  # http://s.webcore.io/aIdT
					'eventlet = web.server.eventlet_:serve[eventlet]', # http://s.webcore.io/aIaa
					'gevent = web.server.gevent_:serve[gevent]',  # http://s.webcore.io/aIpU
					'diesel = web.server.diesel_:serve[diesel]',  # http://s.webcore.io/aIg2
					'bjoern = web.server.bjoern_:serve[bjoern]',  # http://s.webcore.io/aIne
				],
			
			'web.serialize': [
					'json = web.ext.serialize:json.dumps',  # JavaScript Object Notation
					'application/json = web.ext.serialize:json.dumps',  # JavaScript Object Notation
					'yaml = yaml:dumps[yaml]',  # Yet Another Markup Language
					'application/x-yaml = yaml:dumps[yaml]',  # Yet Another Markup Language
				]
		},
	
	# ## Installation Dependencies
	
	setup_requires = [
			'pytest-runner',
		] if {'pytest', 'test', 'ptr'}.intersection(sys.argv) else [],
	install_requires = [
			'marrow.package<2.0',  # dynamic execution and plugin management
			'WebOb',  # HTTP request and response objects, and HTTP status code exceptions
			'pathlib2; python_version < "3.4"',  # Path manipulation utility lib; builtin in 3.4 and 3.5.
		],
	tests_require = tests_require,
	
	extras_require = {
			# ### Recommended Environments
			'development': tests_require + [  # An extended set of useful development tools.
					'ptpython',  # Improved Python shell.  Run as "ptipython".
					'ipython',  # Additional extras to improve the Python shell.
					'pudb',  # Curses-based interactive debugger.
					'backlash',  # Web-based interactive REPL shell and traceback explorer.
					'waitress',  # Recommended development server.
				],
			'production': [  # A default set of production tools.
					'flup6',  # Python 2 and 3 compatible Flup fork.
				],
			
			# ### Dispatch Mechanisms
			'object': ['web.dispatch.object'],
			'route': ['web.dispatch.route'],
			'traversal': ['web.dispatch.traversal'],
			
			# ### General Extras
			'cli': ['web.command'],  # Command-line interface.
			'template': ['web.template', 'cinje'],  # Recommended template engine.
			'database': ['web.db', 'pymongo'],  # Recommended database engine.
			'asset': ['webassets'],  # Recommended static asset management.
			'bson': ['pymongo'],
			'yaml': ['pyyaml'],
			
			# ### Plugin Dependencies
			'waitress': ['waitress'],
			'tornado': ['tornado'],
			'flup': ['flup6'],
			'cherrypy': ['cherrypy'],
			'paste': ['paste'],
			'eventlet': ['eventlet'],
			'gevent': ['gevent'],
			'diesel': ['diesel'],
			'bjoern': ['bjoern'],
		},
)

