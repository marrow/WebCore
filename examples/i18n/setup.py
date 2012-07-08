#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup


setup(
    name="WebCore-Example-i18n",
    version="0.2",
    description="An example of how to use i18n with WebCore.",
    author="Alice Bevan-McGregor",
    author_email="alice@gothcandy.com",
    license="MIT",
    packages=['example'],
    package_data={
        'example': [
            'templates/*.html',
            'locale/LC_MESSAGES/*.mo'
        ]
    },
    zip_safe=False,
    install_requires=['WebCore', 'Babel', 'Beaker', 'Genshi'],
    message_extractors={
        'example': [
            ('**.py', 'python', None),
            ('templates/**.html', 'genshi', None),
        ]
    }
)
