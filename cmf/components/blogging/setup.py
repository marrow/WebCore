#!/usr/bin/env python
# encoding: utf-8

import sys, os
from setuptools import setup, find_packages

__version__ = "$Revision: $"

if sys.version_info <= (2, 5):
    raise SystemExit("Python 2.5 or later is required.")

execfile(os.path.join("cmf", "components", "blog", "release.py"))

setup(
        name = name,
        version = version,
        description = summary,
        long_description = description,
        classifiers = [
                'Development Status :: 3 - Alpha',
                'Environment :: Web Environment',
                'Framework :: Pylons',
                'Framework :: TurboGears',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                'Operating System :: OS Independent',
                'Programming Language :: Python :: 2.5',
                'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        keywords = '',
        author = author,
        author_email = email,
        url = url,
        license = license,
        packages = find_packages(exclude=['ez_setup', 'docs', 'examples', 'tests']),
        include_package_data = True,
        zip_safe = False,
        
        install_requires = [
            ],
        
        entry_points = {
                'turbocmf.component': [
                        "blog = cmf.components.blog:BlogComponent",
                    ]
            },
        
        namespace_packages = [
                'cmf',
                'cmf.components',
            ]
    )
