#!/usr/bin/env python
# encoding: utf-8

import sys, os

try:
    from distribute_setup import use_setuptools
    use_setuptools()

except ImportError:
    pass

from setuptools import setup, find_packages


if sys.version_info <= (2, 5):
    raise SystemExit("Python 2.5 or later is required.")

execfile(os.path.join("web", "release.py"))



setup(
        name = name,
        version = version,
        
        description = summary,
        long_description = description,
        author = author,
        author_email = email,
        url = url,
        download_url = download_url,
        license = license,
        keywords = '',
        
        install_requires = [
                'Paste',
                'PasteDeploy',
                'PasteScript',
                'WebOb',
                'WebError',
                'TemplateInterface'
            ],
        
        test_suite = 'nose.collector',
        tests_require = [
                'nose',
                'coverage',
                'Genshi',
                'SQLAlchemy',
                'Beaker',
                'ToscaWidgets'
            ],
        
        classifiers = [
                "Development Status :: 1 - Planning",
                "Environment :: Console",
                "Framework :: Paste",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
                "Programming Language :: Python",
                "Topic :: Internet :: WWW/HTTP :: WSGI",
                "Topic :: Software Development :: Libraries :: Python Modules"
            ],
        
        packages = find_packages(exclude=['ez_setup', 'examples', 'tests', 'tests.*', 'docs']),
        include_package_data = True,
        package_data = {
                '': ['README.textile', 'LICENSE', 'distribute_setup.py'],
                'docs': ['Makefile', 'source/*']
            },
        zip_safe = True,
        
        namespace_packages = [
                'web',
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
                        'mongo = web.db.mongo:MongoMiddleware'
                    ]
            }
    )
