#!/usr/bin/env python
# encoding: utf-8

import sys, os

try:
    from setuptools import setup, find_packages

except ImportError:
    print "You do not seem to have distribute or setuptools installed."
    print "WebCore requires functionality from one of these packages."
    print "We recommend installing distribute:\n\
        http://pypi.python.org/pypi/distribute#installation-instructions\n"
    
    raise


if sys.version_info <= (2, 5):
    raise SystemExit("Python 2.5 or later is required.")

execfile(os.path.join("web", "release.py"))



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
                'Paste',
                'PasteDeploy',
                'PasteScript',
                'WebOb',
                'WebError',
                'marrow.util < 1.3',
                'marrow.templating'
            ],
        
        test_suite = 'nose.collector',
        tests_require = [
                'nose',
                'coverage',
                'Genshi',
                'Mako',
                'SQLAlchemy',
                'pymongo',
                'MongoEngine',
                'Beaker',
                'ToscaWidgets',
                'Routes',
                'repoze.profile',
                'pyamf'
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
        
        packages = find_packages(exclude=['examples', 'tests', 'tests.*', 'docs']),
        include_package_data = True,
        package_data = {
                '': ['README.textile', 'LICENSE'],
                'docs': ['Makefile', 'source/*']
            },
        zip_safe = True,
        
        namespace_packages = [
                'web',
                'web.app',
                'web.extras',
                'web.db'
            ],
        
        entry_points = {
                'paste.app_factory': [
                        'main = web.core:Application.factory'
                    ],
                'paste.paster_command': [
                        'shell = web.commands.shell:ShellCommand'
                    ],
                'webcore.command': [
                        'shell = web.commands.shell:ShellCommand'
                    ],
                'toscawidgets.host_frameworks': [
                        'webcore = web.extras.twframework:WebCoreHostFramework'
                    ],
                'webcore.db.engines': [
                        'sqlalchemy = web.db.sa:SQLAlchemyMiddleware',
                        'mongo = web.db.mongo:MongoMiddleware',
                        'mongoengine = web.db.me:MongoEngineMiddleware'
                    ]
            }
    )
