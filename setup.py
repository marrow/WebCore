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

from setuptools.command.test import test as TestCommand


if sys.version_info < (2, 7):
	raise SystemExit("Python 2.7 or later is required.")
elif sys.version_info > (3, 0) and sys.version_info < (3, 2):
	raise SystemExit("CPython 3.3 or Pypy 3 (3.2) or later is required.")

version = description = url = author = author_email = ""  # Silence linter warnings.
exec(open(os.path.join("web", "core", "release.py")).read())  # Actually populate those values.


class PyTest(TestCommand):
	__slots__ = ('test_args', 'test_suite')
	
	def finalize_options(self):
		TestCommand.finalize_options(self)
		
		self.test_args = []
		self.test_suite = True
	
	def run_tests(self):
		import pytest
		sys.exit(pytest.main(self.test_args))


here = os.path.abspath(os.path.dirname(__file__))

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-spec',  # output formatting
		'web.dispatch.object',  # dispatch tests
		'backlash',  # debug tests
	]


setup(
	name = "WebCore",
	version = version,
	
	description = description,
	long_description = codecs.open(os.path.join(here, 'README.rst'), 'r', 'utf8').read(),
	url = url,
	download_url = 'http://s.webcore.io/aIly',
	
	author = author.name,
	author_email = author.email,
	
	license = 'MIT',
	keywords = ['marrow', 'web.core'],
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
			"Programming Language :: Python :: 3.3",
			"Programming Language :: Python :: 3.4",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Internet :: WWW/HTTP :: WSGI",
			"Topic :: Software Development :: Libraries :: Python Modules",
		],
	
	packages = find_packages(exclude=['bench', 'docs', 'example', 'test', 'htmlcov']),
	include_package_data = True,
	namespace_packages = [
			'web',  # primary namespace
			'web.app',  # application code goes here
			'web.ext',  # framework extensions
			'web.server',  # front-end WSGI bridges
		],
	
	entry_points = {
			'web.app': [  # Re-usable applications or application components.
					'static = web.app.static:static',
				],
			
			'web.extension': [
					'base = web.ext.base:BaseExtension',
					'request = web.ext.base:BaseExtension',
					'response = web.ext.base:BaseExtension',
					
					'analytics = web.ext.analytics:AnalyticsExtension',
					
					'annotation = web.ext.annotation:AnnotationExtension',  # Preferred use/needs reference.
					'cast = web.ext.annotation:AnnotationExtension',
					'typecast = web.ext.annotation:AnnotationExtension',
					
					'local = web.ext.local:ThreadLocalExtension',  # Preferred use/needs reference.
					'threadlocal = web.ext.local:ThreadLocalExtension',
					
					#' = web.ext.:Extension',
				],
			
			'web.server': [
					# For pure WSGI deployment, where you need the WSGI application itself, use:
					# web.server.application
					# This module exposes the WSGI application under a variety of common names.
					
					'wsgiref = web.server.wsgiref_:serve',  # Python built-in server; single-threaded
					'waitress = web.server.waitress_:serve[waitress]',  # http://s.webcore.io/aIou development server
					'tornado = web.server.tornado_:serve[tornado]',  # http://s.webcore.io/aIaN
					'fcgi = web.server.fcgi:serve[flup]',  # http://s.webcore.io/fhVY recommended production server
					
					# Planned:
					#
					# cgi
					#
					# http://wsgi.readthedocs.org/en/latest/servers.html
					#
					# gae Google App Engine http://s.webcore.io/aIic
					# cherrypy http://s.webcore.io/aIoF
					# paste http://s.webcore.io/aIdT
					# rocket http://s.webcore.io/aIgr
					# gunicorn http://s.webcore.io/aIcy
					# eventlet http://s.webcore.io/aIaa
					# gevent http://s.webcore.io/aIpU
					# diesel http://s.webcore.io/aIg2
					# fapws3 http://s.webcore.io/aIcI
					# twisted http://s.webcore.io/aIgc
					# meinheld http://s.webcore.io/aId1
					# bjoern http://s.webcore.io/aIne
				],
		},
	
	install_requires = [
			'marrow.package<2.0',  # dynamic execution and plugin management
			'WebOb',  # HTTP request and response objects, and HTTP status code exceptions
		],
	
	extras_require = {
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
			
			# Extras similar to Gentoo USE flags.
			'object': ['web.dispatch.object'],
			'route': ['web.dispatch.route'],
			'traversal': ['web.dispatch.traversal'],
			
			# Plugin dependencies.
			'waitress': ['waitress'],
			'tornado': ['tornado'],
			'flup': ['flup6'],
		},
	
	tests_require = tests_require,
	
	dependency_links = [
		],
	
	zip_safe = True,
	cmdclass = dict(
			test = PyTest,
		)
)
