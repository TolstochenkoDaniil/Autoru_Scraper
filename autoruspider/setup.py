# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'autoru',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = autoruSpider.settings']},
    package_data = {'':['log/*.log']},
    include_package_data=False
)