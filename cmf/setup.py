#!/usr/bin/env python
# encoding: utf-8

import sys, os
from setuptools import setup, find_packages

__version__ = "$Revision: $"

if sys.version_info <= (2, 5):
    raise SystemExit("Python 2.5 or later is required.")

execfile(os.path.join("cmf", "release.py"))

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
        test_suite = 'nose.collector',
        
        install_requires = [
                'turbogears2',
                'ToscaWidgets',
                'tw.wymeditor'
            ],
        
        entry_points = {
                'turbocmf.component': [
                        "asset = cmf.components.asset:AssetComponent",
                        "folder = cmf.components.folder:FolderComponent",
                        "page = cmf.components.page.component:PageComponent",
                        "file = cmf.components.file.component:FileComponent",
                        "extension = cmf.components.extension:ExtensionComponent"
                    ],
                'turbocmf.page.renderer': [
                        "raw = cmf.components.page.renderers.raw:RawRenderer",
                        "html = cmf.components.page.renderers.html:HTMLRenderer",
                        "genshi = cmf.components.page.renderers.templated:GenshiRenderer",
                        "rest = cmf.components.page.renderers.rest:RestRenderer"
                    ]
            },
        
        namespace_packages = [
                'cmf',
                'cmf.components',
                'cmf.extensions',
                'cmf.components.file',
                'cmf.components.file.processors',
                'cmf.components.page',
                'cmf.components.page.renderers'
            ]
    )
