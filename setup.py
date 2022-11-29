#!/usr/bin/env python3

from setuptools import setup
from sys import argv, version_info as python_version
from pathlib import Path


if python_version < (3, 6):
	raise SystemExit("Python 3.6 or later is required.")

here = Path(__file__).resolve().parent
version = description = url = author = None  # Populated by the next line.
exec((here / "web" / "core" / "release.py").read_text('utf-8'))

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-isort',  # import ordering
		'web.dispatch.object>=3.0,<4.0',  # dispatch tests
		'backlash',  # debug tests
	]


setup(
	name = "WebCore",
	version = version,
	
	description = description,
	long_description = (here / 'README.rst').read_text('utf-8'),
	url = url,
	download_url = 'https://github.com/marrow/WebCore/releases',
	
	author = author.name,
	author_email = author.email,
	
	license = 'MIT',
	keywords = [
			'marrow',
			'web.core',
			'web.ext',
			'wsgi',
			'web framework',
		],
	classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Environment :: Console",
			"Environment :: Web Environment",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.6",
			"Programming Language :: Python :: 3.7",
			"Programming Language :: Python :: 3.8",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
			"Topic :: Internet :: WWW/HTTP :: WSGI",
			"Topic :: Software Development :: Libraries",
			"Topic :: Software Development :: Libraries :: Application Frameworks",
			"Topic :: Software Development :: Libraries :: Python Modules",
		],
	
	project_urls = {
			"Repository": "https://github.com/marrow/WebCore/",
			"Documentation": "https://github.com/marrow/WebCore/#readme",
			"Issue Tracker": "https://github.com/marrow/WebCore/issues",
			"Funding": "https://www.patreon.com/GothAlice",
		},
	
	# Currently unsupported.
	#document_names = {
	#		"description": "README.rst",
	#		"license": "LICENSE.txt",
	#	},
	#contacts = [
	#		{"name": "Alice Bevan-McGregor", "email": "alice@gothcandy.com", "role": "author"},
	#	],
	#environments = [
	#		"python_version >= '3.2'",
	#		"'3.0' > python_version >= '2.7'",
	#	],
	
	# Code Discovery
	
	packages = (  # Define namaespace package contributions.
			'web.app',  # Application code namaespace.
			'web.core',  # Framework core.
			'web.ext',  # Default extension set.
			'web.server',  # Default WSGI server adapters / bridges.
		),
	include_package_data = True,
	package_data = {'': ['README.rst', 'LICENSE.txt']},
	zip_safe = False,
	
	python_requires = '~=3.6',
	
	setup_requires = [
			'pytest-runner',
		] if {'pytest', 'test', 'ptr'}.intersection(argv) else [],
	
	install_requires = [
			'marrow.package>=2.0.0',  # dynamic execution and plugin management
			'web.dispatch>=3.0.1',  # endpoint discovery
			'WebOb',  # HTTP request and response objects, and HTTP status code exceptions
		],
	
	tests_require = tests_require,
	
	extras_require = {
			# Recommended Environments
			'development': tests_require + [  # An extended set of useful development tools.
					'ptipython',  # Improved Python REPL shell, combination of ptpython and ipython.
					'pudb',  # Curses-based interactive debugger with Borland stylings.
					'backlash',  # Web-based interactive REPL shell and traceback explorer.
					'waitress',  # Recommended development server.
					'pre-commit',  # Commit validation enforcement.
					'bandit',  # Automated vulnerability analysis.
					'e',  # Shell interaction utility.
				],
			'production': [  # A default set of production tools.
					'flup6',  # Python 2 and 3 compatible Flup fork.
				],
			
			# Dispatch Mechanisms
			'object': ['web.dispatch.object~=3.0'],
			'route': ['web.dispatch.route~=2.0'],
			'resource': ['web.dispatch.resource~=3.0'],
			
			# General Extras
			'cli': ['web.command~=3.0'],  # Command-line interface.
			'template': ['cinje~=1.1.2'],  # Recommended template engine.
			'database': ['web.db~=3.0', 'pymongo'],  # Recommended database engine.
			'asset': ['webassets'],  # Recommended static asset management.
			
			# Serializers
			'json': [],  # Nothing extra is required to support JSON; included for completeness.
			'bson': ['pymongo'],
			'yaml': ['pyyaml'],
			'msgpack': ['msgpack'],
			
			# Plugin Dependencies
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
	
	entry_points = {
			# Re-usable applications or application components.
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
			
			# WebCore Extensions
			'web.extension': [
					# BaseExtension, providing request, response, and default views.
					'base = web.ext.base:BaseExtension',
					'request = web.ext.base:BaseExtension',
					'response = web.ext.base:BaseExtension',
					
					# Miscelaneous Builtin Extensions
					'analytics = web.ext.analytics:AnalyticsExtension',
					'annotation = web.ext.annotation:AnnotationExtension',  # Preferred use/needs reference.
					'cast = web.ext.annotation:AnnotationExtension',  # Legacy reference.
					'typecast = web.ext.annotation:AnnotationExtension',  # Legacy reference.
					'local = web.ext.local:ThreadLocalExtension',  # Preferred use/needs reference.
					'threadlocal = web.ext.local:ThreadLocalExtension',  # Legacy reference.
					'assets = web.ext.assets:WebAssetsExtension',  # WebAssets integration.
				],
			
			# WSGI Server Adapters
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
					'application/json+bson = bson.json_util:dumps[bson]',  # MongoDB Extended JSON
					'yaml = yaml:dumps[yaml]',  # Yet Another Markup Language
					'application/x-yaml = yaml:dumps[yaml]',  # Yet Another Markup Language
					'msgpack = msgpack:packb[msgpack]',  # MessagePack
					'application/msgpack = msgpack:unpackb[msgpack]',  # MessagePack
				]
		},
)
