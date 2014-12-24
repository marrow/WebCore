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


if sys.version_info < (2, 6):
	raise SystemExit("Python 2.6 or later is required.")
elif sys.version_info > (3, 0) and sys.version_info < (3, 2):
	raise SystemExit("Python 3.2 or later is required.")

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

tests_require = ['pytest', 'pytest-cov', 'pytest-flakes', 'pytest-cagoule', 'pytest-spec<=0.2.22']


setup(
	name = "WebCore",
	version = version,
	
	description = description,
	long_description = codecs.open(os.path.join(here, 'README.rst'), 'r', 'utf8').read(),
	url = url,
	download_url = 'https://warehouse.python.org/project/WebCore/',
	
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
			"Programming Language :: Python :: 2.6",
			"Programming Language :: Python :: 2.7",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.2",
			"Programming Language :: Python :: 3.3",
			"Programming Language :: Python :: 3.4",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Internet :: WWW/HTTP :: WSGI",
			"Topic :: Software Development :: Libraries :: Python Modules",
		],
	
	packages = find_packages(exclude=['test', 'script', 'example']),
	include_package_data = True,
	namespace_packages = [
			'web',
			'web.app',
			'web.blueprint',
			'web.cli',
			'web.ext',
			'web.rpc',
		],
	
	entry_points = {
			'console_scripts': ['web = web.cli.core:main'],
			'web.command': [
					'versions = web.cli.versions:versions',
					'clean = web.cli.clean:clean',
					'compile = web.cli.compile:compile',
					'serve = web.cli.serve:serve',
					'shell = web.cli.shell:shell',
				],
			'web.dispatch': [
					'object = web.dialect.dispatch:ObjectDispatchDialect',
					'route = web.dialect.route:RoutingDialect',
					'traversal = web.dialect.traversal:TraversalDialect'
				]
		},
	
	install_requires = [
			'marrow.templating',
			'WebOb'
		],
	
	extras_require = dict(
			development = tests_require,
		),
	
	tests_require = tests_require,
	
	dependency_links = [
			'git+https://github.com/illico/pytest-spec.git@feature/py26#egg=pytest-spec-0.2.22'
		],
	
	zip_safe = True,
	cmdclass = dict(
			test = PyTest,
		)
)
