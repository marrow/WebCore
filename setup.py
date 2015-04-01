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
elif sys.version_info > (3, 0) and sys.version_info < (3, 3):
	raise SystemExit("Python 3.3 or later is required.")

exec(open(os.path.join("web", "release.py")).read())


class PyTest(TestCommand):
	def finalize_options(self):
		TestCommand.finalize_options(self)
		
		self.test_args = []
		self.test_suite = True
	
	def run_tests(self):
		import pytest
		sys.exit(pytest.main(self.test_args))


here = os.path.abspath(os.path.dirname(__file__))

contentment_require = [
		'mongoengine==0.9',  # database layer
		'pytz',  # timzone support
		'blinker',  # signals
		'markupsafe',  # injection protection
		'tenjin',  # high-performance template engine
		'babel',  # internationalization and localization
		'scrypt',  # difficult to verify hashes
		'webassets',  # static asset management
		'tablib',  # data interchange
		'xlwt',  # Microsoft Excel data interchange
	]

tests_require = contentment_require + [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-cagoule',  # intelligent test execution
		'pytest-spec<=0.2.22',  # output formatting
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
	keywords = '',
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
	
	packages = find_packages(exclude=['bench', 'docs', 'example', 'test']),
	include_package_data = True,
	namespace_packages = [
			'web',  # primary namespace
			'web.app',  # application code goes here
			'web.ext',  # framework extensions
			'web.server',  # front-end WSGI bridges
		],
	
	entry_points = {
			'web.extension': [
					'base = web.ext.base:BaseExtension',
					'request = web.ext.base:BaseExtension',
					'response = web.ext.base:BaseExtension',
					
					'typecast = web.ext.cast:CastExtension',
					'threadlocal = web.ext.local:ThreadLocalExtension',
					'mail = web.ext.mail:MailExtension',
					'scheduler = web.ext.schedule:APSchedulerExtension',
					'transaction = web.ext.transaction:TransactionExtension',
					#' = web.ext.:Extension',
				],
			
			'web.server': [
					'auto = web.server.automatic:serve',  # detect available server
					
					# For pure WSGI deployment, where you need the WSGI application itself, use:
					# web.server.application
					# This module exposes the WSGI application under a variety of common names.
					
					'wsgiref = web.server.wsgiref_:serve',  # Python built-in server; single-threaded
					'waitress = web.server.waitress_:serve',  # http://s.webcore.io/aIou
					'tornado = web.server.tornado_:serve',  # http://s.webcore.io/aIaN
					'fcgi = web.server.fcgi:serve',  # recommended production interface
					
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
			'WebCore.template<4.0.0',  # extensible template engine support
			'marrow.package<2.0',  # dynamic execution and plugin management
			'WebOb',  # HTTP request and response objects, and HTTP status code exceptions
			'marrow.util<2.0',  # miscelaneous utilities; use of <2.0 is deprecated
			'pyyaml',  # rich data interchange format; used for configuration
		],
	
	extras_require = dict(
			development = tests_require,
			contentment = contentment_require,
			
			# TBD: Required by various sub-components.
			mail = ['marrow.mailer'],
			textile = ['textile'],
			markdown = ['markdown'],
			bbcode = ['bbcode'],
			analytics = ['geoip2', 'user-agents>=0.3.0'],
		),
	
	tests_require = tests_require,
	
	dependency_links = [
			'git+https://github.com/mongoengine/mongoengine.git@master#egg=mongoengine-0.9',
		],
	
	zip_safe = True,
	cmdclass = dict(
			test = PyTest,
		)
)
