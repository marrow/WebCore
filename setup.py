#!/usr/bin/env python

from setuptools import setup, find_packages
import sys, os

if sys.version_info <= (2, 5):
    raise SystemExit("Python 2.5 or later is required.")

execfile(os.path.join("web", "release.py"))
execfile(os.path.join("web", "utils", "distrib.py"))

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
                'PasteScript',
                'PasteDeploy',
                'WebOb',
                'WebError'
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
        
        extras_require = {
                'routes': ["Routes"],
                'sessions': ["Beaker"],
                'cache': ["Beaker"],
                
                # Templating Languages
                'cheetah': ["TurboCheetah"],
                'myghty': ["BuffetMyghty"],
                'kid': ["TurboKid"],
                'genshi': ["Genshi"],
                'jinja2': ['Jinja2'], # TODO: a python.templating.engines compatible entry point
                'json': ['TurboJson'],
                'mako': ['Mako'],
                'string': ['BuffetString'],
                'xslt': ['BuffetXSLT'],
                
                # A sane set of default extras.
                'default': ['Beaker', 'TurboJson', 'Genshi']
            },
        
        classifiers = [
                "Development Status :: 1 - Planning",
                "Environment :: Console",
                "Framework :: Paste",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: BSD License",
                "Operating System :: OS Independent",
                "Programming Language :: Python",
                "Topic :: Internet :: WWW/HTTP :: WSGI",
                "Topic :: Software Development :: Libraries :: Python Modules"
            ],
        
        packages = find_packages(exclude=['ez_setup', 'examples', 'tests', 'tests.*', 'docs']),
        package_data = find_package_data(where='web', package='web'),
        include_package_data = True,
        zip_safe = True,
        
        namespace_packages = [
                'web',
                'web.extras'
            ],
        
        entry_points = {
                'paste.app_factory': [
                        'main = web.core:Application.factory'
                    ],
                'toscawidgets.host_frameworks': [
                        'yapwf = web.extras.twframework:YAPWFHostFramework'
                    ],
                'yapwf.db.engines': [
                        'sqlalchemy = web.db.sa:SQLAlchemyMiddleware',
                        'sqlsoup = web.db.sa:SQLSoupMiddleware'
                    ]
            }
        
#        entry_points = {
#                'paste.paster_command': [
#                        'shell = yapwf.commands:ShellCommand'
#                    ],
#                'paste.paster_create_template': [
#                        'yapwf = yapwf.util:ApplicationTemplate'
#                    ]
#            },
    )
