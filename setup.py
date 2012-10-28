#!/usr/bin/env python
# encoding: utf-8

import sys
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    print("You do not seem to have distribute or setuptools installed.")
    print("WebCore requires functionality from one of these packages.")
    print("We recommend installing distribute:\n\
        http://pypi.python.org/pypi/distribute#installation-instructions\n")

    raise


if sys.version_info <= (2, 6):
    raise SystemExit("Python 2.6 or later is required.")

exec(open(os.path.join("web", "release.py")).read())


setup(
        name = "WebCore",
        version = version,

        description = "A full-stack, light-weight and efficient web development framework.",
        long_description = "",
        author = "Alice Bevan-McGregor and contributors",
        author_email = "alice@gothcandy.com",
        url = "http://www.web-core.org/",
        download_url = "http://cheeseshop.python.org/pypi/WebCore/",
        license = "MIT",
        keywords = '',

        install_requires = [
                'marrow.util < 1.3',
                'marrow.templating',
                'marrow.wsgi.objects'
            ],

        test_suite = 'nose.collector',
        tests_require = [
                'nose',
                'coverage'
            ],

        classifiers = [
                "Development Status :: 5 - Production/Stable",
                "Environment :: Console",
                "Environment :: Web Environment",
                "Framework :: Paste",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
                "Programming Language :: Python",
                "Topic :: Internet :: WWW/HTTP :: WSGI",
                "Topic :: Software Development :: Libraries :: Python Modules"
            ],

        packages = find_packages(exclude=['examples', 'tests', 'tests.*', 'docs', 'scripts']),
        include_package_data = True,
        package_data = {
                '': ['README.textile', 'LICENSE'],
                'docs': ['Makefile', 'source/*']
            },
        zip_safe = True,

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
                        'compile = web.cli.compile:compile'
                    ],
                'web.dispatch': [
                        'object = web.dialect.dispatch:ObjectDispatchDialect',
                        'route = web.dialect.route:RoutingDialect',
                        'traversal = web.dialect.traversal:TraversalDialect'
                    ]
            }
    )
