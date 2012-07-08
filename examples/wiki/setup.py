#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages


setup(
        name="WebCore-Example-Wiki",
        version="0.1",
        description="A WebCore example wiki application.",
        author="Alice Bevan-McGregor",
        author_email="alice@gothcandy.com",
        license="MIT",
        packages=find_packages(),
        include_package_data=False,
        zip_safe=False,

        install_requires=[
                'WebCore',
                'Genshi',
                'SQLAlchemy',
                'textile'
            ],
    )
