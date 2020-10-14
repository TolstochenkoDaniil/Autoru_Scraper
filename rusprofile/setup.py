# Automatically created by: scrapyd-deploy

import os
from importlib.machinery import SourceFileLoader
from pkg_resources import parse_requirements
from setuptools import setup, find_packages

module_name = 'Rusprofile_parser'

module = SourceFileLoader(
    module_name, os.path.join(module_name, '__init__.py')
).load_module()

def load_requirements(fname: str) -> list:
    requirements = []
    with open(fname, 'r') as fp:
        for requirement in parse_requirements(fp.read()):
            extras = '[{}]'.format(','.join(requirement.extras)) if requirement.extras else ''
            requirements.append(
                '{}{}{}'.format(requirement.name,extras,requirement.specifier)
            )
    return requirements

setup(
    name         = module_name,
    version      = module.__version__,
    author=module.__author__,
    description=module.__doc__,
    platforms='Win',
    classifiers=[
        'Operating System :: Win',
        'Programming Language :: Python',
        'Programming Language :: Python 3.8'
    ],
    python_requires='>=3.8',
    packages     = find_packages('rusprofile'),
    entry_points = {'scrapy': ['settings = rusprofile.settings']},
    include_package_data = True,
)