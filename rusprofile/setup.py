# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'rusprofile',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = rusprofile.settings']},
    package_data = {'':['log/*.log']},
    include_package_data=False
)
