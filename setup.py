#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name = "pySpellbook",
    version = "0.7",
    packages = find_packages('src'),
    package_dir = {'':'src'},
    package_data = {'pySpellbook':['templates/html/resources/*','templates/html/template.html']},
    entry_points={
          'console_scripts': [
              'pySpellbook = pySpellbook.qt:run_pyspellbook'
          ]},
    install_requires = ['sqlalchemy',
                        'PySide',
                        'jinja2',
                        'pyquery',
                        'weasyprint',
                        'appdirs']
)
