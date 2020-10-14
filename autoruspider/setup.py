# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'autoruSpider',
    version      = '0.0.1',
    author       = 'Daniil Tolstochenko',
    platforms    = 'all',
    python_requires = '>=3.8',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = autoruSpider.settings']},
    include_package_data = True
)