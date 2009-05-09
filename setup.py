from setuptools import setup, find_packages
import sys, os

if sys.version_info <= (2, 5):
    raise SystemExit("Python 2.5 or later is required.")

execfile(os.path.join("yapwf", "release.py"))

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
                'PasteDeploy'
            ],
        extras_require = {
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
        
        packages = find_packages(exclude=['ez_setup', 'examples', 'tests', 'docs']),
        package_data = find_package_data(where='yapwf', package='yapwf'),
        include_package_data = True,
        zip_safe = True,
        
        test_suite = 'nose.collector',
        tests_require = 'pymta >= 0.3',
        
        namespace_packages = [
                'yapwf',
                'yapwf.extras'
            ]
        
        entry_points = {
            
            },
    )
