from setuptools import setup, find_packages

setup(
        name = "YAPWF-Example-Wiki",
        version = "0.1",
        description = "A YAPWF example wiki application.",
        author = "Alice Bevan-McGregor",
        author_email = "alice@gothcandy.com",
        license = "MIT",
        packages = find_packages(),
        include_package_data = False,
        zip_safe = False,
        
        install_requires = [
                'YAPWF',
                'Genshi',
                'SQLAlchemy',
                'textile'
            ],
        
        namespace_packages = [
                'web',
                'web.extras',
                'web.extras.examples'
            ],
    )
