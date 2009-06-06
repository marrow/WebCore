from setuptools import setup, find_packages

setup(
        name = "YAPWF-Example-Deploy",
        version = "0.1",
        description = "An example of YAPWF using Paste Deploy configuration files.",
        author = "Alice Bevan-McGregor",
        author_email = "alice@gothcandy.com",
        license = "MIT",
        packages = find_packages(),
        include_package_data = False,
        zip_safe = True,
    )
