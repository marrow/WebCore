from setuptools import setup, find_packages

setup(
        name = "YAPWF-Example-i18n",
        version = "0.1",
        description = "An example of YAPWF using Paste Deploy configuration files.",
        author = "Alice Bevan-McGregor",
        author_email = "alice@gothcandy.com",
        license = "MIT",
        packages = find_packages(),
        include_package_data = True,
        package_data = {
                'example': [
                        'templates/*',
                        'i18n/*/LC_MESSAGES/*.mo'
                    ]
            },
        zip_safe = False,
        install_requires = ['YAPWF', 'Babel', 'Beaker', 'Genshi'],
        message_extractors = {
                'example': [
                        ('**.py', 'python', None),
                        ('templates/**.html', 'genshi', None),
                        ('public/**', 'ignore', None)
                    ]
            },
        paster_plugins = ['PasteScript', 'YAPWF']
    )
